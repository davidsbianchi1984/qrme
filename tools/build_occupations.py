#!/usr/bin/env python3
"""Build the occupation pool that ships inside the app.

    python3 tools/build_occupations.py

Writes ``qrme/data/occupations.json`` — one row per position, carrying only
the light half: what the job is called, the **digital skills** a synthetic
one needs to perform it, and the **connections** it must hold to get the
work done. The heavy half — the working knowledge of the profession — is
not here on purpose. `company.study_seat()` fetches that per seat at setup
and stores it for offline use, which is why an exhaustive pool still fits
in a few hundred kilobytes.

## Where this came from

    asked     which roles can a founder open
    mattered  which roles exist

`plan_company` asked a model and, when the answer did not parse, fell back
to three canned seats — "Industry lead", "Front desk", "Bookkeeper". On a
deployment answering from the local stub that fallback *is* the feature,
and the owner's photograph showed exactly those three. A pool the app
carries answers the common case without a model at all, and leaves the
model for the tail.

## Two halves

The families in `occupation_spec.py` are written by hand: each role there
says what makes it that role rather than the one next to it. The lists in
`tools/data` are titles only — the occupation names of the standard
taxonomies, pasted in rather than fetched, because the build environment
cannot reach those hosts. A title from a list is filed into a family by
`title_families.py` and inherits that family's skills and connections, so
it arrives as a real, searchable row rather than a bare string.

Where the two halves name the same job the written one wins: it says more.

## Shape

Families carry what every role in them shares, so a role adds only what
distinguishes it. That keeps the source small enough to read and the
output consistent enough to search.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "qrme" / "data" / "occupations.json"

#: A family is (shared skills, shared connections, {title: (skills, conns)}).
#: A role may add a third entry: the words somebody uses when they do not
#: know the job's name — "reads scans" for the radiologist.
#: Semicolons separate; a role's own entries are added to the family's.
FAMILIES: dict[str, tuple[str, str, dict[str, tuple[str, str]]]] = {}
SYNONYMS: dict[str, str] = {}
WORD_SYNONYMS: dict[str, str] = {}


def family(name: str, skills: str, connections: str,
           roles: dict[str, tuple[str, str]]) -> None:
    FAMILIES[name] = (skills, connections, roles)


def _split(s: str) -> list[str]:
    return [p.strip() for p in s.split(";") if p.strip()]


STOP = {"the", "and", "of", "a", "an", "for", "to", "in", "on", "with",
        "who", "what", "someone", "somebody", "person", "that", "does",
        "keeping", "writing", "handling", "records", "record"}

def _stem(w: str) -> str:
    """Enough stemming that "welding" reaches the welder.

    Not a linguistic stemmer — a suffix chop, applied identically to what
    is typed and to what is indexed, so the two meet in the middle. The
    first version indexed the raw words and matched the raw words, and a
    person searching for what the job *does* ("welding", "bookkeeping")
    found nothing while a person who already knew its name found it. The
    search bar is for the first person.
    """
    for suffix in ("ings", "ing", "ers", "er", "ies", "ied", "ed", "es", "s",
                   "y"):
        if len(w) - len(suffix) >= 4 and w.endswith(suffix):
            return w[: -len(suffix)]
    return w



def _word_extra(title: str) -> str:
    """The layman words any row with this title inherits, by stem."""
    low = title.lower()
    return " ".join(v for stem, v in WORD_SYNONYMS.items() if stem in low)


def _keywords(title: str, skills: list[str], extra: str = "") -> list[str]:
    """What a person might type to find this row.

    The search bar is the way in — "someone who reads scans" has to reach
    the radiologist — so every word of the title and of the skills becomes
    a term. Duplicates and joining words are dropped; nothing else is.
    """
    words: list[str] = []
    for text in [title, *skills, extra, _word_extra(title)]:
        for w in re.findall(r"[a-z0-9]+", text.lower()):
            s = _stem(w)
            if len(w) > 2 and w not in STOP and s not in words:
                words.append(s)
    return words


def build() -> dict:
    """The pool, with everything a family shares stored once.

    A row used to carry its family's skills, connections and their search
    terms in full. With the taxonomy titles folded in that is the same
    eight phrases written out a thousand times over — the file tripled and
    said nothing new. The family block holds the shared half now and a row
    carries only what makes it that row; `occupations._pool` puts the two
    back together on load.
    """
    fams: dict[str, dict] = {}
    rows = []
    seen: set[str] = set()
    for fam, (fs, fc, roles) in FAMILIES.items():
        base_s, base_c = _split(fs), _split(fc)
        fams[fam] = {"s": base_s, "c": base_c, "k": _keywords("", base_s)}
        for title, spec in roles.items():
            rs, rc = spec[0], spec[1]
            extra = spec[2] if len(spec) > 2 else ""
            extra = (extra + " " + SYNONYMS.get(title, "")).strip()
            key = title.lower()
            if key in seen:
                raise SystemExit(f"duplicate position: {title}")
            seen.add(key)
            skills = [x for x in _split(rs) if x not in base_s]
            conns = [x for x in _split(rc) if x not in base_c]
            words = _keywords(title, skills, extra)
            rows.append({"t": title, "f": fam, "s": skills, "c": conns,
                         "k": [w for w in words if w not in fams[fam]["k"]],
                         "w": 1})
    # The group tier. Written roles do not take one: they already say what
    # makes them that role, and a rule keyed on a word in the title cannot
    # improve on a line somebody wrote about the job itself.
    from occupation_groups import SPECIFICS, group_of   # noqa: PLC0415
    groups = {name: {"s": spec["s"], "c": spec["c"],
                     "k": _keywords("", spec["s"])}
              for name, spec in SPECIFICS.items()}

    for title, fam, extra in _imported(seen, rows):
        words = _keywords(title, [], extra)
        row = {"t": title, "f": fam,
               "k": [w for w in words if w not in fams[fam]["k"]]}
        grp = group_of(title)
        if grp:
            row["g"] = grp
            row["k"] = [w for w in row["k"] if w not in groups[grp]["k"]]
        rows.append(row)
    rows.sort(key=lambda r: (r["f"], r["t"]))
    return {"version": 3, "families": fams, "groups": groups,
            "positions": rows}


def _norm(title: str) -> str:
    """A key that reads "Registered Nurses" and "Registered nurse" alike.

    Only ever used to decide whether a list has named a job the families
    already describe. Singular/plural is the whole difference in nearly
    every collision, so that is all this collapses.
    """
    words = []
    for w in re.findall(r"[a-z0-9]+", title.lower()):
        words.append(w[:-1] if w.endswith("s") and not w.endswith("ss") else w)
    return " ".join(words)


PAREN = re.compile(r"^(.*?)\s*\(([^()]*)\)\s*$")

#: Where a title lands when nothing can be read off it. See `_imported`.
LAST_RESORT = "Skilled trades"


def _nearest(rows: list[dict]):
    """Find the occupation a title most resembles, by shared words.

    The taxonomy's reported titles are what workers call themselves, and a
    quarter of them are abbreviations and trade names no word rule will
    ever hold — "ACNP", "AB Watchman", "Sole Skiver". Matching them against
    the occupations already built is better than guessing from the words,
    because a title that shares most of its words with a known row is
    almost always the same work under another name.
    """
    index: dict[str, list[int]] = {}
    stems = []
    for i, row in enumerate(rows):
        own = {_stem(w) for w in re.findall(r"[a-z0-9]+", row["t"].lower())}
        stems.append(own)
        for word in own:
            index.setdefault(word, []).append(i)

    def go(title: str) -> str | None:
        want = {_stem(w) for w in re.findall(r"[a-z0-9]+", title.lower())
                if len(w) > 2}
        tally: dict[int, int] = {}
        for word in want:
            for i in index.get(word, ()):
                tally[i] = tally.get(i, 0) + 1
        if not tally:
            return None
        # Share of the candidate's own words, so a two-word row that
        # matches both beats a six-word row that matches two.
        best = max(tally.items(),
                   key=lambda kv: (kv[1] / max(len(stems[kv[0]]), 1), kv[1]))
        return rows[best[0]]["f"]

    return go


def _imported(written: set[str], rows: list[dict]) -> list[tuple[str, str, str]]:
    """Every title from the lists the families do not already cover.

    Returns (title, family, extra search words). A reported title often
    carries its own expansion — "AC Installer (Air Conditioning
    Installer)" — and that expansion is what somebody would actually type,
    so it becomes search words rather than part of the name.
    """
    from title_families import UNPLACED, by_shape, family_of   # noqa: PLC0415

    nearest = _nearest(rows)
    have = {_norm(t) for t in written}
    out, seen = [], set()
    counts = {"rule": 0, "nearest": 0, "shape": 0, "last": 0}
    for path in sorted((ROOT / "tools" / "data").glob("*_titles.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            match = PAREN.match(line)
            title, extra = (match.group(1).strip(), match.group(2).strip()) \
                if match else (line, "")
            key = _norm(title)
            if not key or key in have or key in seen:
                continue
            fam = family_of(title)
            if fam is not UNPLACED:
                counts["rule"] += 1
            else:
                fam = nearest(title + " " + extra)
                if fam:
                    counts["nearest"] += 1
                else:
                    fam = by_shape(title)
                    if fam:
                        counts["shape"] += 1
                    else:
                        # Nothing left to read: no word the rules know, no
                        # occupation it resembles, not even an agent-noun
                        # ending. What survives all three is overwhelmingly
                        # a trade name — "Whistle Punk", "Straw Boss",
                        # "Hogshead Salvage" — so that is where it lands.
                        # The count is printed rather than swallowed: if it
                        # ever grows, the rules above are what is missing.
                        fam = LAST_RESORT
                        counts["last"] += 1
            seen.add(key)
            out.append((title, fam, extra))
    print(f"  filed by word rule {counts['rule']}, by nearest occupation "
          f"{counts['nearest']}, by title shape {counts['shape']}, "
          f"by last resort {counts['last']}")
    return out


def main() -> None:
    from occupation_spec import SYNONYMS, WORD_SYNONYMS, load   # noqa: PLC0415
    globals()['SYNONYMS'] = SYNONYMS
    globals()['WORD_SYNONYMS'] = WORD_SYNONYMS
    load(family)
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    kb = OUT.stat().st_size / 1024
    grouped = sum(1 for r in data["positions"] if r.get("g"))
    print(f"{len(data['positions'])} positions in {len(data['families'])} "
          f"families — {kb:.0f} KB")
    print(f"{grouped} carry a group ({100 * grouped / len(data['positions']):.1f}%) "
          f"across {len(data['groups'])} groups")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
