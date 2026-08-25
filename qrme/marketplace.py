"""Marketplace search: words, place, and a hand with the words.

`GET /marketplace/listings` filtered by exact kind, exact tag and exact
subject area, which works only if you already know the vocabulary. Three
things are added here, and the third is the one with a rule attached.

**Words.** :func:`search` takes a free-text query and scores it across title,
tags, blurb and provider, so "someone who can help me read a lease" finds a
legal listing without the searcher knowing the tag is `legal`.

**Place.** A listing can say where it is offered — and this is *not*
`listings.area`, which is a subject area (healthcare, finance, relationships).
Conflating them would make "near me" mean "in healthcare". Geography lives in
its own table, coarse and typed:

* **Nothing is sniffed.** No IP geolocation, no GPS, no address parsing. A
  seller types where they serve; a searcher types where they are. Location
  that a user did not type is location they did not agree to share.
* **A rated listing can never carry a place.** :func:`set_place` refuses one,
  so no row exists, so no place filter can ever match it. That is the same
  line docs/desks.md draws — where a performer physically is has nothing to do
  with browsing them — made structural instead of checkable.

**A hand with the words.** :func:`assist` will talk to somebody who cannot
name what they want and hand back *query suggestions*. It returns suggestions
and never results: the model writes a search box's contents, the searcher
decides whether to run it, and the ranking they get is the same deterministic
ranking everyone else gets.

That boundary is the whole design. A marketplace where a model silently
re-ranks what you are shown is one where nobody — including the operator —
can say why you saw what you saw. So there is no code path from
:func:`assist` to :func:`search`; the caller carries the text across, or does
not.

See docs/marketplace.md.
"""

from __future__ import annotations

import json
import re

from . import db, i18n

SCOPES = ("locality", "region", "anywhere")
KINDS = ("profile", "content", "expertise", "service")

# Field weights for the text score. Title beats tags beats blurb, because a
# word in the title is what the listing is, and a word in the blurb is
# something it mentions.
_WEIGHTS = {"title": 6, "tags": 4, "provider_name": 3, "blurb": 2, "area": 1}

# Words too common to rank on. Kept short deliberately — a long stop list
# starts eating meaningful terms in a marketplace of specialists.
_STOP = {"a", "an", "and", "the", "for", "with", "who", "can", "help", "me",
         "my", "i", "to", "of", "in", "on", "at", "is", "are", "someone",
         "somebody", "need", "want", "looking", "find"}

MAX_SUGGESTIONS = 3


class MarketError(Exception):
    pass


def _words(s: str | None) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9']+", (s or "").lower())
            if w not in _STOP and len(w) > 1]


# --- where a listing is offered -------------------------------------------

def _listing(listing_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM listings WHERE id=?", (listing_id,)).fetchone()
    return dict(row) if row else None


def _is_rated(row: dict) -> bool:
    if not row.get("profile_id"):
        return False
    p = db.connect().execute("SELECT adult_mode FROM profiles WHERE id=?",
                             (row["profile_id"],)).fetchone()
    return bool(p and p["adult_mode"])


def set_place(listing_id: str, locality: str, region: str | None = None,
              remote: bool = False) -> dict:
    """Say where a listing is offered.

    Refused for a rated listing, and refused rather than silently ignored: an
    operator who thinks they have set a location needs to be told they have
    not. Because the refusal happens here, no place row can exist for a rated
    listing, and therefore no place filter can surface one.
    """
    row = _listing(listing_id)
    if row is None:
        raise MarketError("no such listing")
    if not locality.strip():
        raise MarketError("a place needs a locality — 'somewhere' is what "
                          "leaving it unset already means")
    if _is_rated(row):
        raise MarketError(
            "a rated listing cannot carry a location: where a performer "
            "physically is has nothing to do with browsing them, and a place "
            "filter is a way of asking")

    conn = db.connect()
    conn.execute(
        "INSERT INTO listing_places (listing_id, locality, region, remote,"
        " created_at) VALUES (?,?,?,?,?)"
        " ON CONFLICT (listing_id) DO UPDATE SET locality=excluded.locality,"
        " region=excluded.region, remote=excluded.remote",
        (listing_id, locality.strip(), (region or "").strip() or None,
         int(remote), db.utcnow()))
    conn.commit()
    return place_of(listing_id)


def place_of(listing_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM listing_places WHERE listing_id=?",
        (listing_id,)).fetchone()
    if row is None:
        return None
    return {"listing_id": row["listing_id"], "locality": row["locality"],
            "region": row["region"], "remote": bool(row["remote"])}


def clear_place(listing_id: str) -> dict:
    conn = db.connect()
    conn.execute("DELETE FROM listing_places WHERE listing_id=?", (listing_id,))
    conn.commit()
    return {"listing_id": listing_id, "place": None}


def localities() -> list[dict]:
    """Every place a listing actually claims, with counts.

    Offered instead of a free-text place box on its own, so a searcher picks
    from what exists rather than typing a spelling nothing matches and
    concluding the marketplace is empty.
    """
    rows = db.connect().execute(
        "SELECT locality, region, COUNT(*) AS n FROM listing_places"
        " GROUP BY locality, region ORDER BY n DESC, locality").fetchall()
    return [{"locality": r["locality"], "region": r["region"],
             "listings": r["n"]} for r in rows]


# --- settings --------------------------------------------------------------

def prefs(interactor_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM marketplace_prefs WHERE interactor_id=?",
        (interactor_id,)).fetchone()
    if row is None:
        return {"interactor_id": interactor_id, "locality": None,
                "region": None, "scope": "anywhere", "include_remote": True,
                "kinds_wanted": [], "tags": [], "updated_at": None}
    return {"interactor_id": row["interactor_id"], "locality": row["locality"],
            "region": row["region"], "scope": row["scope"],
            "include_remote": bool(row["include_remote"]),
            "kinds_wanted": json.loads(row["kinds"]),
            "tags": json.loads(row["tags"]),
            "updated_at": row["updated_at"]}


def set_prefs(interactor_id: str, *, locality=None, region=None, scope=None,
              include_remote=None, kinds=None, tags=None) -> dict:
    cur = prefs(interactor_id)
    scope = scope or cur["scope"]
    if scope not in SCOPES:
        raise MarketError(i18n.fill(i18n.MUST_BE_ONE_OF, field="scope", choices=', '.join(SCOPES)))
    bad = [k for k in (kinds or []) if k not in KINDS]
    if bad:
        raise MarketError(i18n.fill(i18n.UNKNOWN_LISTING_KINDS, got=bad))
    # Narrowing to a place you have not named would return nothing and look
    # like an empty marketplace, so say what is actually wrong.
    place = locality if locality is not None else cur["locality"]
    reg = region if region is not None else cur["region"]
    if scope == "locality" and not place:
        raise MarketError("scope 'locality' needs a locality to be near")
    if scope == "region" and not (reg or place):
        raise MarketError("scope 'region' needs a region")

    new = {
        "locality": place, "region": reg, "scope": scope,
        "include_remote": cur["include_remote"] if include_remote is None
        else bool(include_remote),
        "kinds_wanted": cur["kinds_wanted"] if kinds is None else list(kinds),
        "tags": cur["tags"] if tags is None else list(tags),
    }
    conn = db.connect()
    conn.execute(
        "INSERT INTO marketplace_prefs (interactor_id, locality, region,"
        " scope, include_remote, kinds, tags, updated_at)"
        " VALUES (?,?,?,?,?,?,?,?)"
        " ON CONFLICT (interactor_id) DO UPDATE SET locality=excluded.locality,"
        " region=excluded.region, scope=excluded.scope,"
        " include_remote=excluded.include_remote, kinds=excluded.kinds,"
        " tags=excluded.tags, updated_at=excluded.updated_at",
        (interactor_id, new["locality"], new["region"], new["scope"],
         int(new["include_remote"]), json.dumps(new["kinds_wanted"]),
         json.dumps(new["tags"]), db.utcnow()))
    conn.commit()
    return prefs(interactor_id)


# --- search ----------------------------------------------------------------

def _score(row: dict, tags: list[str], terms: list[str]) -> tuple[int, list[str]]:
    if not terms:
        return 0, []
    fields = {"title": row["title"], "blurb": row["blurb"],
              "provider_name": row["provider_name"], "area": row["area"],
              "tags": " ".join(tags)}
    score, hit = 0, []
    for field, value in fields.items():
        words = set(_words(value))
        for t in terms:
            # Prefix rather than exact, so "nutrition" finds "nutritionist".
            if any(w == t or w.startswith(t) or t.startswith(w) for w in words):
                score += _WEIGHTS[field]
                if field not in hit:
                    hit.append(field)
    return score, hit


def search(q: str | None = None, *, kind: str | None = None,
           tag: str | None = None, area: str | None = None,
           scope: str = "anywhere", locality: str | None = None,
           region: str | None = None, include_remote: bool = True,
           adult_viewer: bool = False, limit: int = 50) -> dict:
    """Rank listings against a query and a place. Deterministic, always.

    No model touches this. Two callers with the same arguments get the same
    order, which is what makes "why am I seeing this?" answerable — the
    response carries the terms that matched and the fields they hit.
    """
    if scope not in SCOPES:
        raise MarketError(i18n.fill(i18n.MUST_BE_ONE_OF, field="scope", choices=', '.join(SCOPES)))
    if scope == "locality" and not locality:
        raise MarketError("scope 'locality' needs a locality")
    if scope == "region" and not (region or locality):
        raise MarketError("scope 'region' needs a region")

    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM listings ORDER BY created_at DESC, rowid DESC"
    ).fetchall()
    places = {p["listing_id"]: p for p in (
        dict(r) for r in conn.execute("SELECT * FROM listing_places").fetchall())}

    terms = _words(q)
    out, filtered_by_place = [], 0
    for r in rows:
        row = dict(r)
        tags = json.loads(row["tags"])
        if kind and row["kind"] != kind:
            continue
        if tag and tag.lower() not in [t.lower() for t in tags]:
            continue
        if area and (row["area"] or "").lower() != area.lower():
            continue
        if row["profile_id"] and not adult_viewer and _is_rated(row):
            continue                      # rated never surfaces unverified

        place = places.get(row["id"])
        if scope != "anywhere":
            remote_ok = include_remote and place and place["remote"]
            if not remote_ok:
                if place is None:
                    filtered_by_place += 1
                    continue
                if scope == "locality":
                    if place["locality"].lower() != locality.lower():
                        filtered_by_place += 1
                        continue
                else:
                    want = (region or locality or "").lower()
                    if (place["region"] or "").lower() != want:
                        filtered_by_place += 1
                        continue

        score, hit = _score(row, tags, terms)
        if terms and score == 0:
            continue
        out.append({
            "id": row["id"], "kind": row["kind"], "title": row["title"],
            "blurb": row["blurb"], "tags": tags, "area": row["area"],
            "provider_name": row["provider_name"],
            "business": bool(row["business"]), "profile_id": row["profile_id"],
            "place": {"locality": place["locality"], "region": place["region"],
                      "remote": place["remote"]} if place else None,
            "score": score, "matched_on": hit,
        })

    out.sort(key=lambda x: -x["score"])          # stable: recency breaks ties
    return {
        "query": q, "terms": terms, "scope": scope,
        "locality": locality, "region": region,
        "results": out[:limit], "total": len(out),
        "hidden_by_place": filtered_by_place,
        "ranking": ("deterministic — title, tags, provider, blurb, in that "
                    "order. No model reorders this."),
    }


def search_with_prefs(interactor_id: str | None, q: str | None = None,
                      **over) -> dict:
    """Search using an interactor's saved settings as the defaults.

    Their settings are defaults, not a cage: anything passed explicitly wins,
    so a saved locality never traps somebody who has typed a different one.
    """
    if interactor_id:
        p = prefs(interactor_id)
        # `setdefault` is wrong here: the route passes every query parameter,
        # so an unset one arrives as an explicit None and the key already
        # exists. A saved setting has to fill a None, not just a gap.
        for key in ("scope", "locality", "region", "include_remote"):
            if over.get(key) is None:
                over[key] = p[key]
        # A single saved kind or tag narrows; several mean "any of these",
        # which this filter cannot express, so it stays open rather than
        # silently picking one of them.
        if over.get("kind") is None and len(p["kinds_wanted"]) == 1:
            over["kind"] = p["kinds_wanted"][0]
        if over.get("tag") is None and len(p["tags"]) == 1:
            over["tag"] = p["tags"][0]
    over = {k: v for k, v in over.items() if v is not None}
    return search(q, **over)


# --- a hand with the words -------------------------------------------------

_ASSIST_SYSTEM = (
    "You help somebody turn a vague need into a short marketplace search. "
    "Reply with two or three candidate searches, one per line, each at most "
    "six words, using plain words a listing would contain. No numbering, no "
    "explanation, no preamble."
)


def _fallback_suggestions(need: str) -> list[str]:
    """Written-out suggestions for when no model is reachable.

    The keywords carry, so the box is never empty and the searcher is never
    stuck behind a provider outage.
    """
    terms = _words(need)[:4]
    out = []
    if terms:
        out.append(" ".join(terms[:3]))
        if len(terms) > 1:
            out.append(terms[0])
    return out or ["expertise"]


def assist(need: str, *, interactor_id: str | None = None,
           provider=None) -> dict:
    """Turn "I don't know what to search for" into candidate searches.

    Returns suggestions and **never results**. The searcher picks one, edits
    it, or ignores all three, and the search they then run is the same
    deterministic one everybody else gets. There is deliberately no code path
    from here into :func:`search`.
    """
    if not (need or "").strip():
        raise MarketError("say what you are trying to find, in your own words")

    suggestions, source = [], "local"
    if provider is not None:
        try:
            reply = provider.generate(
                _ASSIST_SYSTEM, [{"role": "user", "content": need.strip()}])
            lines = [ln.strip(" -•\t").strip() for ln in
                     (reply or "").splitlines() if ln.strip()]
            suggestions = [ln for ln in lines if 0 < len(ln) <= 60]
            if suggestions:
                source = "model"
        except Exception:
            suggestions = []
    if not suggestions:
        suggestions = _fallback_suggestions(need)

    out = {
        "need": need.strip(),
        "suggestions": suggestions[:MAX_SUGGESTIONS],
        "source": source,
        "ai": source == "model",
        "applied": False,
        "note": ("these are suggestions for the search box — nothing has been "
                 "searched, filtered or reordered on your behalf"),
    }
    if interactor_id:
        p = prefs(interactor_id)
        out["your_settings"] = {"scope": p["scope"], "locality": p["locality"],
                                "region": p["region"]}
    return out
