"""Robotics catalog — the physical bodies a profile can inhabit.

A registry of robot platforms, from full humanoids to home robots to
autonomous vacuums and quadrupeds. Mirrors the connected-apps catalog pattern
(``catalog.py``): a static, auditable table the routers validate against,
shared verbatim across QRME, JIM-mini, and PDI so a robot bound in one product
means the same thing in the others.

``llm_capable`` marks platforms that can run an onboard language model; the
binding then records *which* provider (from the ``qrme.llm`` registry) the
robot is loaded with, so the same persona speaks through the same model
wherever it is embodied.

Commands are validated against a per-kind allowlist — a vacuum cannot be told
to "fetch", and nothing outside the list ever reaches a robot.

## The list covers the market, including what you cannot buy yet

An owner choosing a body is shopping, and a catalogue that shows only what is
already on sale is a worse answer than one that says *this exists, it is not
out yet*. So ``availability`` is part of every row:

``shipping``
    Buyable now, by somebody. Includes developer- and enterprise-only
    platforms — the constraint is money and paperwork, not time.
``preorder``
    Announced with a price and an order book open.
``announced``
    Publicly shown by its maker with no order book. Real, dated, and not yet
    a thing you can hold.

**Only ``shipping`` and ``preorder`` bodies can be bound.** An announced
platform is listed so an owner can see it coming and cannot bind a profile to
a body nobody has — the refusal names the status rather than pretending the
model is unknown, which is what a plain 404 would have said.

This table is a **curated snapshot**, not a feed. ``REVIEWED`` dates it, and
`test_the_body_market.py` fails when that date goes stale — a catalogue whose
`announced` rows shipped two years ago is worse than no catalogue, because it
reads as current. Nothing here is an endorsement, a price, or a claim about
whether a given platform will ever arrive.
"""

from __future__ import annotations

#: When this table was last checked against what the makers were saying.
#: `test_the_body_market.py` fails once this is more than a year behind the
#: newest changelog entry — a catalogue that reads as current and is not is
#: worse than none, because `announced` is a claim about the future.
REVIEWED = "2026-07-31"

#: Availability, in the only three states that matter to somebody choosing a
#: body. See the module docstring; `announced` cannot be bound.
BUYABLE = ("shipping", "preorder")

# (key, label, maker, kind, capabilities, llm_capable, availability)
_ROWS: list[tuple[str, str, str, str, list[str], bool, str]] = [
    # --- humanoids -------------------------------------------------------
    ("neo", "NEO", "1X Technologies", "humanoid",
     ["mobility", "manipulation", "voice", "vision", "chores"], True,
     "preorder"),
    ("digit", "Digit", "Agility Robotics", "humanoid",
     ["mobility", "manipulation", "vision", "logistics"], True, "shipping"),
    ("apollo", "Apollo", "Apptronik", "humanoid",
     ["mobility", "manipulation", "vision", "logistics"], True, "shipping"),
    ("figure_02", "Figure 02", "Figure AI", "humanoid",
     ["mobility", "manipulation", "voice", "vision", "logistics"], True,
     "shipping"),
    ("figure_03", "Figure 03", "Figure AI", "humanoid",
     ["mobility", "manipulation", "voice", "vision", "chores"], True,
     "announced"),
    ("optimus", "Optimus", "Tesla", "humanoid",
     ["mobility", "manipulation", "vision", "chores"], True, "announced"),
    ("atlas", "Atlas (electric)", "Boston Dynamics", "humanoid",
     ["mobility", "manipulation", "vision", "logistics"], True, "announced"),
    ("g1", "Unitree G1", "Unitree Robotics", "humanoid",
     ["mobility", "manipulation", "vision"], True, "shipping"),
    ("h1", "Unitree H1", "Unitree Robotics", "humanoid",
     ["mobility", "manipulation", "vision"], True, "shipping"),
    ("r1", "Unitree R1", "Unitree Robotics", "humanoid",
     ["mobility", "vision"], True, "shipping"),
    ("gr_2", "GR-2", "Fourier Intelligence", "humanoid",
     ["mobility", "manipulation", "vision"], True, "shipping"),
    ("walker_s2", "Walker S2", "UBTech Robotics", "humanoid",
     ["mobility", "manipulation", "vision", "logistics"], True, "shipping"),
    ("u1_lite", "UWorld U1 Lite", "UBTech Robotics", "humanoid",
     ["mobility", "voice", "vision"], True, "shipping"),
    ("u1_pro", "UWorld U1 Pro", "UBTech Robotics", "humanoid",
     ["mobility", "manipulation", "voice", "vision"], True, "shipping"),
    ("u1_ultra", "UWorld U1 Ultra", "UBTech Robotics", "humanoid",
     ["mobility", "manipulation", "voice", "vision", "chores"], True,
     "shipping"),
    ("a2", "A2", "AgiBot", "humanoid",
     ["mobility", "manipulation", "voice", "vision"], True, "shipping"),
    ("k2", "Kepler K2", "Kepler Robotics", "humanoid",
     ["mobility", "manipulation", "vision"], True, "shipping"),
    ("phoenix", "Phoenix", "Sanctuary AI", "humanoid",
     ["mobility", "manipulation", "vision"], True, "announced"),
    ("iron", "IRON", "XPENG Robotics", "humanoid",
     ["mobility", "manipulation", "voice", "vision"], True, "announced"),
    ("oli", "Oli", "LimX Dynamics", "humanoid",
     ["mobility", "manipulation", "vision"], True, "preorder"),

    # --- home robots -----------------------------------------------------
    ("isaac_1", "Isaac 1", "Weave Robotics", "home_robot",
     ["mobility", "manipulation", "voice", "vision", "tidying"], True,
     "preorder"),
    ("memo", "Memo", "Sunday Robotics", "home_robot",
     ["mobility", "manipulation", "voice", "vision", "tidying"], True,
     "preorder"),
    ("astro", "Astro", "Amazon", "home_robot",
     ["mobility", "voice", "vision", "camera_patrol"], True, "shipping"),
    ("ballie", "Ballie", "Samsung", "home_robot",
     ["mobility", "voice", "vision", "projection"], True, "announced"),
    ("q9", "Q9", "LG Electronics", "home_robot",
     ["mobility", "voice", "vision"], True, "announced"),

    # --- quadrupeds ------------------------------------------------------
    ("spot", "Spot", "Boston Dynamics", "quadruped",
     ["mobility", "vision", "inspection", "camera_patrol"], True, "shipping"),
    ("go2", "Go2", "Unitree Robotics", "quadruped",
     ["mobility", "vision", "inspection"], True, "shipping"),
    ("b2", "B2", "Unitree Robotics", "quadruped",
     ["mobility", "vision", "inspection", "logistics"], True, "shipping"),

    # --- vacuums ---------------------------------------------------------
    ("saros_20", "Saros 20", "Roborock", "vacuum",
     ["mapping", "navigation", "vacuum", "mop", "camera_patrol"], True,
     "shipping"),
    ("saros_20_sonic", "Saros 20 Sonic", "Roborock", "vacuum",
     ["mapping", "navigation", "vacuum", "sonic_mop", "camera_patrol"], True,
     "shipping"),
    ("qrevo_curv_2_flow", "Qrevo Curv 2 Flow", "Roborock", "vacuum",
     ["mapping", "navigation", "vacuum", "mop"], False, "shipping"),
    ("x50_ultra", "X50 Ultra", "Dreame", "vacuum",
     ["mapping", "navigation", "vacuum", "mop", "camera_patrol"], True,
     "shipping"),
    ("deebot_x8", "Deebot X8 Pro Omni", "Ecovacs", "vacuum",
     ["mapping", "navigation", "vacuum", "mop", "camera_patrol"], True,
     "shipping"),
    ("roomba_max_705", "Roomba Max 705", "iRobot", "vacuum",
     ["mapping", "navigation", "vacuum", "mop"], False, "shipping"),
    ("narwal_flow", "Flow", "Narwal", "vacuum",
     ["mapping", "navigation", "vacuum", "mop"], False, "shipping"),
    ("matic", "Matic", "Matic Robots", "vacuum",
     ["mapping", "navigation", "vacuum", "mop"], True, "shipping"),
]

BY_KEY: dict[str, dict] = {
    key: {"model": key, "label": label, "maker": maker, "kind": kind,
          "capabilities": caps, "llm_capable": llm, "availability": avail,
          "bindable": avail in BUYABLE}
    for key, label, maker, kind, caps, llm, avail in _ROWS
}

# What each kind of body may be told to do. Everything else is refused.
COMMANDS: dict[str, list[str]] = {
    "humanoid": ["say", "come_here", "follow", "fetch", "tidy", "patrol",
                 "dock", "stop"],
    "home_robot": ["say", "come_here", "follow", "fetch", "tidy", "patrol",
                   "dock", "stop"],
    "vacuum": ["clean", "spot_clean", "patrol", "dock", "locate", "stop"],
    "quadruped": ["come_here", "follow", "patrol", "inspect", "dock", "stop"],
}

# How a robot kind maps onto the existing embodiment kinds.
EMBODIMENT_KIND = {"humanoid": "humanoid", "home_robot": "robot",
                   "vacuum": "robot", "quadruped": "robot"}


def catalog() -> dict:
    """The full registry, grouped three ways, for the catalog endpoint.

    By maker, by kind and by availability — because those are the three
    questions somebody choosing a body actually asks, and grouping in the
    client would mean three clients doing it three ways.
    """
    makers: dict[str, list[dict]] = {}
    kinds: dict[str, list[dict]] = {}
    avail: dict[str, list[dict]] = {}
    for row in BY_KEY.values():
        makers.setdefault(row["maker"], []).append(row)
        kinds.setdefault(row["kind"], []).append(row)
        avail.setdefault(row["availability"], []).append(row)
    return {"robots": list(BY_KEY.values()), "by_maker": makers,
            "by_kind": kinds, "by_availability": avail,
            "commands": COMMANDS, "reviewed": REVIEWED,
            "buyable": list(BUYABLE),
            "note": "a curated snapshot, not a feed. `announced` platforms "
                    "are listed so you can see them coming and cannot be "
                    "bound — there is no body to bind to yet."}


def bindable(model: str) -> bool:
    """Whether a body can be attached to a profile today.

    An announced platform is a real machine somebody has shown and nobody can
    buy. Listing it is useful; letting an owner bind a profile to it is not,
    because every command afterwards would go nowhere.
    """
    spec = BY_KEY.get(model)
    return bool(spec and spec["bindable"])


def get(model: str) -> dict | None:
    return BY_KEY.get(model)


def allowed_commands(model: str) -> list[str]:
    spec = BY_KEY.get(model)
    return COMMANDS.get(spec["kind"], []) if spec else []
