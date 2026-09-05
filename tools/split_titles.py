"""Split a pasted, comma-separated occupation list into one title per line.

A plain split on commas is wrong: many titles carry internal commas
("Cooks, Fast Food"; "Airline Pilots, Copilots, and Flight Engineers").
Three facts recover the boundaries.

    the list is sorted   a title must sort after the one before it
    a serial comma       "…, and X" needs three items, never two
    a qualifier is a     a tail is either lowercase ("and Hearing
    tail, not a title    Officers") or a short capitalised qualifier
                         ("All Other", "Postsecondary", "Except …")

Sorted order does the real work, so the four places where the source
list is itself out of order are declared below rather than left for the
solver to paper over with a merge — which is exactly what it did before
they were named, quietly gluing two occupations into one.

Validated against the 392 titles transcribed by hand: it reproduces them
byte for byte.
"""
from __future__ import annotations

import functools
import sys
from pathlib import Path

sys.setrecursionlimit(20000)   # one frame per fragment

MAXJOIN = 7
FLAT = {"all other", "postsecondary", "hand", "general", "all other specialists"}
QUALIFIER_PREFIX = ("except ", "including ")

# Fragments that begin a title even though they sort before the one
# before them. Each is a spot where the pasted list is out of order.
OUT_OF_ORDER = {
    "Electro-Mechanical and Mechatronics Technologists and Technicians",
    "Hydroelectric Plant Technicians",
    "Personal Care Aides",
    "Psychologists",
}


def may_start(frag: str) -> bool:
    """Can this fragment begin a title, or is it only ever a tail?"""
    low = frag.lower()
    if not frag[:1].isupper():
        return False
    return low not in FLAT and not low.startswith(QUALIFIER_PREFIX)


def split(text: str) -> list[str]:
    frags = [f.strip() for f in text.replace("\n", " ").split(",") if f.strip()]
    n = len(frags)
    reset = {i for i, f in enumerate(frags) if f in OUT_OF_ORDER}

    def joins(i: int):
        if not may_start(frags[i]):
            return []
        out = []
        for k in range(1, MAXJOIN + 1):
            if i + k > n:
                break
            if k > 1 and (i + k - 1) in reset:
                break                                   # a reset point starts a title
            part = frags[i:i + k]
            if k == 2 and part[1].lower().startswith("and "):
                continue                                # a serial comma needs three
            out.append((", ".join(part), i + k, k))
        return out

    @functools.lru_cache(maxsize=None)
    def solve(i: int, prev: str):
        """Most titles covering frags[i:], every one sorting after prev."""
        if i == n:
            return (0, 0, ())
        best = None
        for title, j, k in joins(i):
            if i not in reset and title.lower() <= prev:
                continue
            sub = solve(j, title.lower())
            if sub is None:
                continue
            cand = (sub[0] + 1, k, (title,) + sub[2])
            if best is None or cand[:2] > best[:2]:
                best = cand
        return best

    res = solve(0, "")
    if res is None:
        raise SystemExit("no segmentation of this paste is consistent")
    return list(res[2])


def main() -> None:
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if text.lstrip().startswith("Here"):
        text = text.split("\n", 1)[1]
    titles = split(text)
    sys.stderr.write(f"{len(titles)} titles\n")
    print("\n".join(titles))


if __name__ == "__main__":
    main()
