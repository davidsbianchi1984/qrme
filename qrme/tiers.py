"""Membership: what an account has paid for, and what that entitles it to.

Three plans and a doorway. **Free** ($0) is the whole app with your data in
the clear. **Basic** ($20/month) is the same app in the encrypted vault —
twenty dollars buys *privacy*, not capability, and that is the product
decision `qrme/storage.py` encodes. **Pro** ($130/month) adds the things that
reach outside your own account: the marketplace, connectors, lent skills,
downloads, standing connections, and every modifier and builder. Below all
three is **visitor**, which is not a plan and costs nothing: somebody who
scanned a beacon and landed on a page.

Free and Basic reaching the same capabilities is deliberate. A free tier
crippled into uselessness teaches nobody anything about the product; a free
tier that is honestly *not private* teaches somebody exactly what they are
choosing between — and :data:`storage.FREE_DISCLOSURE` rides on every surface
that stores something, so the choice is legible at the moment it matters
rather than in a Terms of Service.

Visitor is a real state rather than an oversight. QRME's whole reach story is a
stranger scanning a printed code and arriving somewhere useful — a wall that
asked them to subscribe before they could read the page would break the feature
the beacons exist for. So a visitor may read every public surface and create
nothing.

**Money here is simulated**, exactly as in :mod:`qrme.commerce`: subscribing
writes a real row and moves no real funds, and every response that names a
price says so in its own body. A tier system that quietly looked like a working
payment processor would be the one place in this repository where the
simulation was not disclosed, which is precisely where somebody would be misled.

**Enforcement is one table and one chokepoint, not a check per route.**

That is the whole design. :data:`GATED` maps a path prefix and method to the
capability it needs, and :func:`gate` is installed once as an application-wide
dependency. A capability cannot be added to the product and forgotten at one of
its eleven routes, because no route opts in — they are all already covered, and
the question is only what the table says. The alternative was a
``require_plan(...)`` call at the top of every gated handler, which is the
shape this repository has already been bitten by twice: a docstring claiming a
check that the code did not make.

The consequence worth stating: **adding a route under a gated prefix gates it
automatically.** That is the intended direction. A new marketplace endpoint
should be behind the marketplace entitlement by default, and a new one that
should *not* be goes in :data:`OPEN` by name, where somebody can see it.

**Browsing stays open, and that is a decision rather than a gap.** A basic
member may look at the marketplace and cannot list, sell, license or buy on it.
A paywall that hides the shop from the person you are trying to sell to is a
paywall that argues against itself, and the catalogue is public to strangers
anyway — hiding it from paying members but not from passers-by would be
incoherent. So the gate is on the write, and `GET` under a gated prefix is
allowed unless the prefix is listed in :data:`READ_ALSO_GATED`.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

from . import db

# What a plan costs and what it is called. Monthly, both.
PLANS: dict[str, dict] = {
    "visitor": {
        "price_usd": 0,
        "period": None,
        "title": "Visitor",
        "means": "read any public page. Scanning a beacon needs no account.",
    },
    "free": {
        "price_usd": 0,
        "period": None,
        "title": "Free",
        "means": "the same app as Basic, with your data in the clear. No "
                 "vault, nothing encrypted under a key you hold, and the "
                 "people running this deployment can read it.",
    },
    "basic": {
        "price_usd": 20,
        "period": "month",
        "title": "Basic",
        "means": "the same features as Free, in the encrypted vault. Twenty "
                 "dollars buys privacy, not capability.",
    },
    "pro": {
        "price_usd": 130,
        "period": "month",
        "title": "Pro",
        "means": "everything in Basic, plus the marketplace, connectors, "
                 "skills, downloads, connections, and every modifier and "
                 "builder for your agent.",
    },
}
ORDER = ("visitor", "free", "basic", "pro")
# What creating a profile enrols a new account on.
#
# Free rather than Basic, and the change is deliberate: putting somebody on a
# paid plan they did not ask for is the wrong default even when the price is
# fair, and `storage.FREE_DISCLOSURE` means the cheaper default is also the
# honest one — they are told plainly what they got.
DEFAULT_PLAN = "free"

# Every capability, the plan it starts at, and the sentence a refusal returns.
# The refusal names the plan, because "upgrade to continue" with no price is
# the pattern people have learned to distrust.
CAPABILITIES: dict[str, dict] = {
    # Free and Basic reach exactly the same capabilities. That is the product
    # decision: twenty dollars buys privacy rather than features, and a free
    # tier crippled into uselessness teaches nobody anything about the
    # product. See qrme/storage.py.
    "profiles": {
        "from": "free",
        "is": "create and run your own synthetic profiles",
    },
    "own_agent": {
        "from": "free",
        "is": "your own personal agent",
    },
    "builders": {
        "from": "pro",
        "is": "every modifier and builder for your agent — steering, "
              "adaptation, governance and delegation",
    },
    "marketplace": {
        "from": "pro",
        "is": "list, sell, license, place and buy on the marketplace",
    },
    "downloads": {
        "from": "pro",
        "is": "install knowledge packs and downloads",
    },
    "connectors": {
        "from": "pro",
        "is": "connect outside apps and services to a profile",
    },
    "skills": {
        "from": "pro",
        "is": "lend a skill to another profile, or borrow one",
    },
    "connections": {
        "from": "pro",
        "is": "standing connections to other accounts",
    },
}

# Path pattern -> capability. First match wins.
#
# Patterns rather than prefixes, and the difference is not cosmetic: most paid
# capabilities here hang off a profile — `/profiles/{id}/steering`,
# `/profiles/{id}/marketplace` — and a table keyed on the start of the path
# cannot say that without gating the whole `/profiles` tree. The first cut used
# prefixes and named `/steering`, `/governance` and `/licensing`, none of which
# is a route on this application. Every one of them was a paywall in front of a
# wall: it reads as protection, protects nothing, and survives precisely
# because nothing fails. `test_every_gated_pattern_is_a_route_that_exists` is
# what caught them, and is why the table is checked against the served routes
# rather than proof-read.
#
# This is the enforcement, not a description of it. See the module note.
GATED: tuple[tuple[str, str], ...] = (
    (r"^/marketplace(/|$)", "marketplace"),
    (r"^/orders(/|$)", "marketplace"),
    (r"^/subscriptions(/|$)", "marketplace"),
    (r"^/licenses(/|$)", "marketplace"),
    (r"^/placements(/|$)", "marketplace"),
    (r"^/profiles/[^/]+/marketplace(/|$)", "marketplace"),
    (r"^/profiles/[^/]+/licenses?(/|$)", "marketplace"),
    (r"^/packs(/|$)", "downloads"),
    (r"^/connectors(/|$)", "connectors"),
    (r"^/apps(/|$)", "connectors"),
    (r"^/skill-grants(/|$)", "skills"),
    (r"^/grants(/|$)", "skills"),
    (r"^/profiles/[^/]+/grants(/|$)", "skills"),
    (r"^/people/[^/]+/skill-grants(/|$)", "skills"),
    (r"^/surfaces/[^/]+/[^/]+/skill-grants(/|$)", "skills"),
    (r"^/connections(/|$)", "connections"),
    (r"^/handoffs(/|$)", "builders"),
    (r"^/profiles/[^/]+/steering(/|$)", "builders"),
    (r"^/robots/[^/]+/steering(/|$)", "builders"),
)

# Gated patterns where reading is gated too, because the read *is* the feature.
# Empty on purpose, and the emptiness is the decision recorded in the module
# note: browsing the shop is how somebody decides to pay for it.
READ_ALSO_GATED: tuple[str, ...] = ()

# Routes matching a gated pattern that are deliberately not gated, by exact
# method and path. Named here rather than quietly absent, so the exception is
# visible to whoever reads the table.
OPEN: tuple[tuple[str, str], ...] = (
    # Operator setup, not a member purchase. These populate the deployment's
    # starter catalogue — the thing a download is later taken *from* — so
    # gating them would leave a fresh install with an empty shop until
    # somebody bought a plan to stock it.
    ("POST", "/packs/seed"),
    ("POST", "/marketplace/seed"),
    # A search helper that suggests searches and runs none. Searching is
    # browsing, and browsing stays open; a POST here is a read wearing the
    # wrong verb.
    ("POST", "/marketplace/assist"),
)

WRITE_METHODS = ("POST", "PUT", "PATCH", "DELETE")


class TierError(ValueError):
    """A capability this account's plan does not include."""


def _rank(plan: str) -> int:
    return ORDER.index(plan) if plan in ORDER else 0


def plan_of(account_id: str) -> str:
    """The plan this account holds. Visitor until they enrol."""
    row = db.connect().execute(
        "SELECT plan FROM memberships WHERE account_id=? AND ended_at IS NULL",
        (account_id,)).fetchone()
    return row["plan"] if row else "visitor"


def plan_of_profile(profile_id: str) -> str:
    """The plan governing a profile's stored work — its owner's.

    A membership belongs to the person, not the profile (`account_of` explains
    why at length), so anything asking "may this profile's work be sealed" has
    to resolve through `profiles.owner_id` first. Asking `plan_of(profile_id)`
    would find no membership under a profile id, return "visitor", and quietly
    treat every paying member's profile as an open-cloud account.
    """
    row = db.connect().execute(
        "SELECT owner_id FROM profiles WHERE id=?", (profile_id,)).fetchone()
    return plan_of(row["owner_id"]) if row else "visitor"


def entitles(plan: str, capability: str) -> bool:
    """Whether a plan reaches a capability. Pure — no database, so the pricing
    page and the gate cannot disagree about what a plan includes."""
    if capability not in CAPABILITIES:
        raise TierError(f"unknown capability {capability!r}")
    return _rank(plan) >= _rank(CAPABILITIES[capability]["from"])


def includes(plan: str) -> list[str]:
    """Everything a plan reaches, for a pricing page that is generated rather
    than typed — a feature list written by hand is one that goes stale the
    first time a capability moves between plans."""
    return [c for c in CAPABILITIES if entitles(plan, c)]


def may(account_id: str, capability: str) -> bool:
    return entitles(plan_of(account_id), capability)


def refusal(plan: str, capability: str) -> str:
    """Why this was refused, and what would fix it, with the price named."""
    need = CAPABILITIES[capability]["from"]
    spec = PLANS[need]
    return (f"{CAPABILITIES[capability]['is'].capitalize()} needs "
            f"{spec['title']} (${spec['price_usd']}/{spec['period']}). "
            f"This account is on {PLANS[plan]['title']}. "
            "Billing here is simulated — subscribing records a row and moves "
            "no real funds.")


def require(account_id: str, capability: str) -> None:
    plan = plan_of(account_id)
    if not entitles(plan, capability):
        raise TierError(refusal(plan, capability))


def capability_for(method: str, path: str) -> str | None:
    """The capability a request needs, or None if it needs none.

    The single place the mapping is read, so the gate, the pricing page and the
    test that binds them are all looking at one answer.
    """
    import re

    if (method.upper(), path) in OPEN:
        return None
    for pattern, capability in GATED:
        if re.search(pattern, path):
            if method.upper() in WRITE_METHODS or pattern in READ_ALSO_GATED:
                return capability
            return None
    return None


def account_of(request: Request) -> str | None:
    """Whose membership governs this request.

    An owner token's subject is a *profile* id, and a membership belongs to the
    person, so this resolves through to `profiles.owner_id`. Getting that wrong
    in the other direction would be the expensive mistake: a per-profile
    membership would mean somebody paying twice to hold two profiles, which is
    exactly the thing `identity.py` was built to let people do for free.

    An interactor is not an account. Somebody talking to a profile they do not
    own has nothing to be entitled to here, and returning their id would
    silently give every interactor a visitor membership under their own name.
    """
    from . import auth

    who = auth.principal(request)
    if who is None or who.get("role") != "owner":
        return None
    row = db.connect().execute(
        "SELECT owner_id FROM profiles WHERE id=?",
        (who["subject_id"],)).fetchone()
    return row["owner_id"] if row else None


def gate(request: Request) -> None:
    """The chokepoint. Installed once, application-wide.

    Raises 402 rather than 403, and the distinction is worth keeping: 403 says
    *you may not*, 402 says *not on this plan*. A client can act on the second
    by showing a price, and this repository already returns 403 for real
    authorization failures, so collapsing them would make the upgrade prompt
    fire on somebody else's profile.
    """
    capability = capability_for(request.method, request.url.path)
    if capability is None:
        return
    account = account_of(request)
    if account is None:
        # No owner token: either anonymous or an interactor. Authorization is
        # the route's own business and it will answer with 401/403 — a
        # membership refusal here would tell a stranger which plan a feature
        # needs before telling them they are not signed in, which is the wrong
        # order and leaks nothing useful.
        return
    plan = plan_of(account)
    if not entitles(plan, capability):
        # A structured detail rather than a sentence, because 402 is already
        # spoken here for a different thing: `POST /packs/{id}/install`
        # answers 402 for "this pack costs money, confirm the price". Both are
        # genuinely payment-required, so the status is right for both — but a
        # client has to show *upgrade* for one and *confirm* for the other,
        # and telling them apart by matching on prose is the kind of coupling
        # that breaks when somebody rewords a message.
        raise HTTPException(402, {
            "reason": "plan",
            "capability": capability,
            "needs": CAPABILITIES[capability]["from"],
            "have": plan,
            "price_usd": PLANS[CAPABILITIES[capability]["from"]]["price_usd"],
            "period": PLANS[CAPABILITIES[capability]["from"]]["period"],
            "message": refusal(plan, capability),
            "billing": "simulated — no real funds move",
        })


def subscribe(account_id: str, plan: str) -> dict:
    """Enrol, or change plan. Simulated billing, disclosed in the response.

    Changing plan replaces the live row rather than stacking a second one: an
    account on two plans at once is a question nobody should have to answer at
    the point a gate is being checked.
    """
    if plan not in PLANS or plan == "visitor":
        raise TierError(
            f"unknown plan {plan!r}; one of "
            f"{', '.join(p for p in PLANS if p != 'visitor')}")
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "UPDATE memberships SET ended_at=? WHERE account_id=? AND"
        " ended_at IS NULL", (now, account_id))
    conn.execute(
        "INSERT INTO memberships (id, account_id, plan, started_at)"
        " VALUES (?,?,?,?)",
        (db.new_id("mem"), account_id, plan, now))
    conn.commit()
    return membership(account_id)


def cancel(account_id: str) -> dict:
    """End the membership. The account becomes a visitor and keeps its
    profiles — a lapsed subscription is not a reason to delete somebody's
    work, and a product that deleted it would be one nobody could safely try.
    """
    conn = db.connect()
    conn.execute(
        "UPDATE memberships SET ended_at=? WHERE account_id=? AND"
        " ended_at IS NULL", (db.utcnow(), account_id))
    conn.commit()
    return membership(account_id)


def membership(account_id: str) -> dict:
    from . import storage

    plan = plan_of(account_id)
    spec = PLANS[plan]
    return {
        "storage": storage.describe(plan),
        "account_id": account_id,
        "plan": plan,
        "title": spec["title"],
        "price_usd": spec["price_usd"],
        "period": spec["period"],
        "includes": includes(plan),
        "locked": [c for c in CAPABILITIES if not entitles(plan, c)],
        "billing": "simulated — no real funds move; the subscription is a row",
    }


def catalogue() -> dict:
    """The pricing page, generated from the same table the gate reads."""
    from . import storage

    return {
        "plans": [
            {"plan": p, **PLANS[p], "includes": includes(p),
             "locked": [c for c in CAPABILITIES if not entitles(p, c)],
             "storage": storage.describe(p)}
            for p in ORDER],
        "the_difference": storage.vocabulary()["the_difference"],
        "capabilities": CAPABILITIES,
        "billing": "simulated — no real funds move; the subscription is a row",
    }
