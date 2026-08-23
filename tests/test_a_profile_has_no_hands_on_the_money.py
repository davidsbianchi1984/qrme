"""Nothing a profile does on its own can spend money.

    asked     is there an ask-first gate in front of the profile's spending
    mattered  can a profile reach money at all

It cannot, and that is a better answer than a gate. This went looking for
somewhere to put an ask-first confirmation and found nothing to put one in
front of: every path that moves money starts at an HTTP route holding a
person's token, and none of them is reachable from the code a profile runs.

The property is worth a guard precisely BECAUSE nothing enforces it. It is
true by the shape of the code rather than by a check, which means no single
line has to be deleted for it to stop being true — somebody adds a workflow
phase that buys the thing it drafted, or a lookout that renews a subscription
it noticed lapsing, and the money surface has quietly grown a door with
nobody having decided that.

## What counts as the profile acting on its own

Five roots, and the reason each is here:

* `workflows`   — the multi-phase agent. It runs unattended across sessions.
* `companion`   — the profile reaching into somebody's day.
* `lookout`     — the watched pages, woken by the vault's own scheduler.
* `delegation`  — a workflow somebody ELSE started on the profile's behalf.
* `persona`     — whatever the model is told it is, on any turn.

A chat turn belongs on that list in spirit and is checked through `persona`,
which every turn's prompt is built from. The person started the conversation;
what the model then decides to do inside it is exactly the thing this file is
about.

## What counts as money

Every write to the ledger and every purchase. Read as *calls*, not as a list
of module names — a list would be a second place to update, and the day
somebody forgets is the day the guard stops covering the module that grew a
credit.
"""

from __future__ import annotations

import ast
import collections
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1] / "qrme"
MODULES = {p.stem: p for p in PKG.glob("*.py")}

#: The calls that move money. `ledger.credit` is the one write to the ledger;
#: the two commerce doors are the ones a person walks through to spend.
MOVES_MONEY = ("ledger.credit", "commerce.purchase", "commerce.gift(")

#: Where the profile's own conduct starts. See the module docstring.
AUTONOMOUS = ("workflows", "companion", "lookout", "delegation", "persona")


def _imports(path: Path) -> set[str]:
    """Sibling modules this one pulls in, however it spells the import."""
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.level:
            found |= {a.name for a in node.names if a.name in MODULES}
            if node.module in MODULES:
                found.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                tail = alias.name.split(".")[-1]
                if alias.name.startswith("qrme.") and tail in MODULES:
                    found.add(tail)
    return found


def _closure(start: str) -> set[str]:
    """Every module reachable from `start`, transitively.

    Imports rather than a call graph, and deliberately so: it over-reports.
    A module that is imported and never called still counts as reachable
    here, so the guard fails early and loudly rather than depending on this
    file being able to follow a dispatch it cannot see.
    """
    seen: set[str] = set()
    queue = collections.deque([start])
    while queue:
        name = queue.popleft()
        if name in seen or name not in MODULES:
            continue
        seen.add(name)
        queue.extend(_imports(MODULES[name]))
    return seen


def _touches_money(name: str) -> bool:
    body = MODULES[name].read_text(encoding="utf-8")
    return any(call in body for call in MOVES_MONEY)


@pytest.mark.parametrize("root", AUTONOMOUS)
def test_the_profiles_own_conduct_cannot_reach_the_money(root):
    assert root in MODULES, f"{root} is gone — this guard is measuring nothing"
    reached = sorted(m for m in _closure(root) if _touches_money(m))
    assert not reached, (
        f"a profile acting through `{root}` can now reach money, via: "
        + ", ".join(reached)
        + "\n  Nothing asked for this. If a profile is to spend, that is a "
          "decision somebody makes on purpose — with the owner asked first "
          "— rather than a module that turned out to be imported."
    )


def test_the_roots_are_real_and_still_do_something():
    """A guard whose roots have been renamed measures nothing and passes
    quietly, which is worse than not having it."""
    for root in AUTONOMOUS:
        assert root in MODULES, root
        assert len(_closure(root)) > 1, (
            f"{root} imports no siblings at all — either it was gutted or "
            "this file is reading the wrong package"
        )


def test_money_is_read_as_calls_rather_than_a_list_of_modules():
    """The calls above have to actually appear somewhere, or the guard is
    searching for a string the product stopped using and finding it
    nowhere — which passes, forever, for the wrong reason."""
    for call in MOVES_MONEY:
        assert any(call in p.read_text(encoding="utf-8")
                   for p in PKG.rglob("*.py")), (
            f"nothing calls {call!r} any more — this guard is looking for "
            "money in a place the product no longer keeps it"
        )


def test_every_ledger_credit_sits_behind_a_route():
    """The other direction. Money moving is fine; money moving without a
    person's token behind it is not, and the router package is where a
    token is checked."""
    offenders = []
    for path in PKG.rglob("*.py"):
        if "ledger.credit" not in path.read_text(encoding="utf-8"):
            continue
        rel = path.relative_to(PKG)
        if rel.parts[0] == "routers" or path.stem == "ledger":
            continue
        # A module outside the routers may still hold a credit, but only if
        # nothing autonomous can reach it — which is what the parametrised
        # test above proves. Recorded here so the two stay in step.
        offenders.append(str(rel))
    unreachable = set()
    for root in AUTONOMOUS:
        unreachable |= _closure(root)
    reachable_offenders = [o for o in offenders
                           if Path(o).stem in unreachable]
    assert not reachable_offenders, (
        "these hold a ledger credit AND are reachable from the profile's "
        "own conduct: " + ", ".join(reachable_offenders)
    )
