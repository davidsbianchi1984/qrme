"""One search onto the open web — what the agent screen's opener stands on.

"Search the Internet" existed as a sentence before it existed as a
capability. The research excursion next door is a different thing — a model
goes and *studies*, and what it brings back is prose — and it needs a model
configured, which the beta deployment this was asked from does not have.

    asked     can the screen offer a web search
    mattered  does pressing it search the web

So this module is a search, not an inference: the query goes out, titles and
links come back, and no model sits in between. It works on a deployment with
no key of any kind configured, which is exactly the deployment that asked.

## The engine, and why this one

DuckDuckGo's Instant Answer API is keyless and returns JSON. Keyless is the
point: there is no credential to hold, so there is nothing to leak, nothing
to bill, and nothing for a deployment to configure before the button works.
What crosses the wire is the query and nothing else — never who asked, never
the profile's memory — and the visit is witnessed like every other trip off
this host, attributed to the profile whose errand it is.

The trade is honest and written down: an instant-answer engine returns
abstracts and related topics, not the full ten blue links. The payload
carries ``more_url`` — the same search on the engine's own page — so the
screen can always offer the rest rather than pretending this is all there
was.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from . import i18n, offline

_HOST = "https://api.duckduckgo.com"
_MORE = "https://duckduckgo.com"

#: How many rows a screen gets. The engine's related topics can run long,
#: and a phone screen is the reader.
MAX_RESULTS = 8

#: Queries longer than this are cut, not refused — a search engine trimming
#: a query is ordinary behaviour, and a refusal here would make the one
#: button that needs no setup the one that argues.
MAX_QUERY = 400


class SearchError(ValueError):
    """A search refusal, in a sentence a person can act on."""


def _fetch(url: str, on_behalf_of: str) -> dict:
    """One call to the engine. Split out so a test can stand in for the
    network without standing in for any of the rules around it.

    The offline check lives here, at the socket, for the reason `visits`
    gives: a second caller added tomorrow inherits it instead of
    remembering it.
    """
    offline.allow(url, "a web search", on_behalf_of)
    req = urllib.request.Request(url, headers={"user-agent": "qrme"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise SearchError(i18n.fill(i18n.SEARCH_REFUSED,
                                    code=exc.code)) from exc
    except (urllib.error.URLError, ValueError) as exc:
        raise SearchError(
            "the search engine could not be reached from this deployment"
        ) from exc


def _rows(raw: dict) -> list[dict]:
    """The engine's shape, flattened to the one shape a screen renders.

    Instant answers arrive as an abstract plus nested related topics; a
    client should not need to know that. One row shape — ``title``, ``url``,
    ``note`` — always all three keys, empty strings where the engine had
    nothing, because a payload that grows keys only when something is found
    hands every shell ``undefined`` on the case it meets most.
    """
    rows: list[dict] = []
    if raw.get("AbstractText") and raw.get("AbstractURL"):
        rows.append({"title": raw.get("Heading") or "",
                     "url": raw["AbstractURL"],
                     "note": raw["AbstractText"]})

    def walk(items):
        for item in items or []:
            if "Topics" in item:
                yield from walk(item["Topics"])
            elif item.get("FirstURL"):
                yield item

    for item in walk(raw.get("RelatedTopics")):
        if len(rows) >= MAX_RESULTS:
            break
        text = item.get("Text") or ""
        title, _, rest = text.partition(" - ")
        rows.append({"title": title or text,
                     "url": item["FirstURL"],
                     "note": rest})
    return rows


def search(profile_id: str, q: str) -> dict:
    """The query out, rows back, and always a way to the rest.

    ``more_url`` is present on every answer including the empty one — an
    instant-answer engine finding nothing is not the web having nothing,
    and the screen's honest fallback is the engine's own results page.
    """
    q = (q or "").strip()[:MAX_QUERY]
    if not q:
        raise SearchError("nothing to search for — say a few words first")
    url = _HOST + "/?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "no_html": "1", "skip_disambig": "1"})
    raw = _fetch(url, profile_id)
    return {"q": q,
            "engine": "duckduckgo",
            "pages": _rows(raw),
            "more_url": _MORE + "/?" + urllib.parse.urlencode({"q": q})}
