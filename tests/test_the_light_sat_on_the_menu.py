"""Nothing the console pins to the bottom of the glass may cover the menu.

## The report

    "It seems to be blocking the PDI menus"

A photograph of the PDI beta on a phone: the vault light sitting squarely
over the first three tabs of the bottom bar, taking the taps. A second
photograph, one state along — *"Same thing with the small green circle when
minimized"* — showed the minimized light doing it as a 40px disc.

This console's corner widgets were moved above the tab bar in an earlier
round, after the same complaint about the agent lights and the help bubble.
The behaviour was right here and the question was not asked here, which is
the shape `guard_divergences.txt` exists to catch: a fix that travelled and
a guard that did not. The stylesheet is now read in all three products.

## Why nothing caught it

Both halves were correct on their own. The light is `position: fixed` at
`bottom: 22px`, which on a desktop is empty page margin. The sidebar becomes
a bottom bar under `@media (max-width: 760px)`, which is the ordinary way to
put navigation on a phone. Neither rule knows about the other, and no test
in this suite had ever read the stylesheet — the console's guards all ask
what a screen *says*, and this was a question about where a thing *sits*.

    asked     is every screen wired, translated and reachable
    mattered  can the person's thumb reach the tab under the light

## What this checks

The bar's height was read out of the stylesheet rather than written here,
so the clearance tracked the bar. Then the bar itself was retired — the
owner's report called the fifty-six-door bottom rail what it was, and the
menu became a drawer opened from the top-left. The question this file asks
survives the redesign in a new shape: the menu must still win. Nothing the
console pins to the glass may sit *over* an open drawer, which is a
question of stacking rather than of height — so the drawer's z-index is
read out of the stylesheet and every pinned widget has to stack below it.

## The third shape

The widgets were then folded into one thing. Three corners — the help
bubble bottom-right, the agent lights bottom-left, the footsteps chip
top-right — became one stack of tabs on the right edge, the *edge dock*,
after the owner's photographs showed all three sitting on screens again
("they seem to be getting in the way a lot ... maybe horizontal tabs on
the side of the screen that can be moved up or down that you click onto
expand"). The question survives a third time: the docks are pinned to the
glass, so they must stack under the drawer; their tabs are tap targets, so
they must be thumb-sized on a phone; and their panels must stay inside the
glass rather than push the page sideways. The owner kept the round watch
face as what the lights open to, and made the light itself a tab — a
stoplight, minimized — so the circle is a panel now, opened by a press and
gone on the next, never parked; and the footsteps count left the console
altogether, since everyone with an account shows in Discover.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CSS = REPO / "app" / "src" / "styles.css"

#: The breakpoint at which the sidebar becomes a bottom bar.
_MOBILE_HEAD = "@media (max-width: 760px) {"


def _stylesheet() -> str:
    """The stylesheet with its comments removed.

    Prose is not a selector, and this file's comments contain commas — the
    first draft split a selector list on them and read half a sentence as a
    rule name.
    """
    return re.sub(r"/\*.*?\*/", "", CSS.read_text(encoding="utf-8"), flags=re.S)


def _braced(text: str, head: str) -> str:
    """The body of a `head { … }` block, counting braces rather than
    stopping at the first `}` — a media query is full of nested rules, and
    the first draft of this guard read one of them and called it the block.
    """
    start = text.index(head) + len(head)
    depth, i = 1, start
    while depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start:i - 1]


def _mobile_block() -> str:
    """Every block written at the breakpoint, joined.

    A stylesheet may open the same media query more than once — the corner
    widgets in two of these consoles are styled in a block of their own at
    the bottom of the file, on purpose, so that the cascade gives them the
    win. Reading only the first block would measure a rule that a later one
    overrides and call it the answer.
    """
    css = _stylesheet()
    assert _MOBILE_HEAD in css, (
        "the mobile media query is gone from styles.css, so this guard is "
        "reading nothing — find the breakpoint and re-point it")
    blocks, rest = [], css
    while _MOBILE_HEAD in rest:
        body = _braced(rest, _MOBILE_HEAD)
        blocks.append(body)
        rest = rest.split(_MOBILE_HEAD + body + "}", 1)[1]
    return "\n".join(blocks)


def _base() -> str:
    """The stylesheet with its media queries removed, so a rule read here is
    the one that applies on a desktop."""
    css = _stylesheet()
    while _MOBILE_HEAD in css:
        body = _braced(css, _MOBILE_HEAD)
        css = css.replace(_MOBILE_HEAD + body + "}", "", 1)
    return re.sub(r"@media[^{]*\{", "", css)


def _rule(block: str, selector: str) -> str | None:
    """Every declaration written for one selector, or None when absent.

    A selector may be written more than once — the light's mobile rules are
    a shared `bottom` and its own `max-width` — so the readings are merged
    rather than taking the first and calling the rest absent.
    """
    found = [m.group(2) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", block)
             if selector in [s.strip() for s in m.group(1).split(",")]]
    return " ".join(found) if found else None


def _declared() -> dict[str, str]:
    """What `:root` declares, so a value written as a variable can be read.

    The clearance is no longer a literal: the bar measures itself and
    publishes `--tabbar-h`, and `:root` declares the height a browser
    without a ResizeObserver gets. That declaration is the floor this guard
    can check — the measured value is only ever the true height, and the
    true height is what the rule is trying to clear.
    """
    root = re.search(r":root\s*\{([^}]*)\}", _stylesheet())
    body = root.group(1) if root else ""
    return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", body))


def _resolve(value: str) -> str:
    """`var(--x)` replaced by what `:root` says, or by its own fallback."""
    declared = _declared()
    return re.sub(
        r"var\((--[a-z0-9-]+)(?:,\s*([^()]*))?\)",
        lambda m: declared.get(m.group(1), m.group(2) or ""), value)


def _px(declarations: str, prop: str) -> float | None:
    m = re.search(rf"\b{prop}:\s*([^;]+);", declarations)
    if not m:
        return None
    value = _resolve(m.group(1))
    # `calc(var(--tabbar-h) + 12px + env(safe-area-inset-bottom))` — every
    # term adds, and the safe-area term is a phone's home indicator, so the
    # px terms summed are the floor of what the rule reserves. Reading only
    # the first px here read the 12px gap as the whole clearance and called
    # a rule that clears the bar by 88px a lid on the menu.
    if " - " not in value and "min(" not in value and "max(" not in value:
        terms = re.findall(r"(\d+(?:\.\d+)?)px", value)
        if terms:
            return sum(float(t) for t in terms)
    # `calc(76px + env(safe-area-inset-bottom))` — the safe-area term is a
    # phone's home indicator and only ever adds, so the literal px is the
    # floor of what the rule reserves.
    px = re.search(r"(\d+(?:\.\d+)?)px", value)
    return float(px.group(1)) if px else None


def _int(declarations: str, prop: str) -> float | None:
    m = re.search(rf"\b{prop}:\s*(\d+(?:\.\d+)?)\s*;", declarations)
    return float(m.group(1)) if m else None


def _drawer_z() -> float:
    """The menu drawer's stacking level, from the stylesheet's own numbers.

    The mobile sidebar is the drawer: `position: fixed`, slid off-canvas by
    a transform until `.open`. If those rules disappear, the menu has
    changed shape again and a person should re-point this guard rather than
    let it pass on nothing.
    """
    block = _mobile_block()
    sidebar = _rule(block, ".sidebar")
    assert sidebar, (
        "the drawer's rules have been renamed — this guard reads the mobile "
        "`.sidebar`, and cannot see it")
    assert "position: fixed" in sidebar and "transform" in sidebar, (
        "the mobile sidebar is no longer a fixed drawer — the menu changed "
        "shape again, and this guard needs a person to look at what covers "
        "what now")
    z = _int(sidebar, "z-index")
    assert z is not None, ".sidebar no longer declares a z-index to measure"
    return z


#: The four guards below keep the names they had when the widgets sat in
#: the corners — `shared_guards.txt` carries those names across the three
#: products, and a renamed guard reads as a missing one there. What each
#: asks is the question in the dock's shape; the docstrings say which.
#:
#: Everything the shell pins to the glass. A new one is a new row here,
#: which is the point: the question is asked of the class of thing, not of
#: the one that was reported.
PINNED = (".edge-dock", ".edge-panel")


def test_the_stylesheet_still_pins_these_to_the_bottom():
    """The guard on the guard. If the dock stopped being fixed — or was
    renamed — every assertion below would pass on an empty reading."""
    css = _base()
    rule = _rule(css, ".edge-dock")
    assert rule, ".edge-dock is not in styles.css any more"
    assert "position: fixed" in rule and re.search(r"\bright:\s*0", rule), (
        ".edge-dock is no longer fixed to the right edge of the viewport — "
        "either this list is stale or the dock moved, and both want a "
        "person to look")
    panel = _rule(css, ".edge-panel")
    assert panel and "position: absolute" in panel, (
        ".edge-panel no longer hangs off the dock — where it opens is "
        "somebody's decision again")


@pytest.mark.parametrize("selector", PINNED)
def test_nothing_fixed_to_the_bottom_covers_the_bar(selector):
    """The defect, in the menu's current shape.

    The navigation is a drawer now, not a band of the screen, so a pinned
    widget cannot sit *beside* it — it can only sit *over* it, by stacking
    higher. Each widget's z-index therefore has to stay below the drawer's,
    wherever the widget declares one; a widget declaring none stacks at
    auto, which the fixed drawer's own level already beats.

    The name is kept although the bar is gone, deliberately: the three
    products carry this guard by name, and the divergence ledger reads
    names. What is asked is the same question the field report asked —
    can the person's thumb reach the menu under the light.
    """
    drawer = _drawer_z()
    for block in (_base(), _mobile_block()):
        rule = _rule(block, selector)
        if not rule:
            continue
        z = _int(rule, "z-index")
        if z is not None:
            assert z < drawer, (
                f"{selector} stacks at {z} and the menu drawer at {drawer}, "
                "so an open menu sits under the dock — the field report "
                'that produced this guard read "It seems to be blocking '
                'the PDI menus"')


#: What a thumb has to be able to hit. The blanket
#: `button { min-height: 44px }` in the phone block is where this
#: number comes from, and a tab is a button like any other.
TAP_MIN_PX = 44.0

def test_a_tab_is_a_thumb_target_on_a_phone():
    """The tabs lose their words on a phone and keep their glyphs, and a
    control that shrank to its glyph is exactly the one a thumb misses. The
    phone block has to give the tab its full height back, in the rule and
    not by inheritance — `min-height` beats `height`, and the base rule
    sets both to 36."""
    rule = _rule(_mobile_block(), ".edge-tab")
    assert rule, (
        ".edge-tab has no rule at the mobile breakpoint, so it keeps its "
        "desktop size on a phone")
    for prop in ("height", "min-height"):
        size = _px(rule, prop)
        assert size is not None and size >= TAP_MIN_PX, (
            f"a dock tab is {size}px {prop} on a phone, under the "
            f"{TAP_MIN_PX}px every other control here gets")


def test_the_minimized_light_is_a_dot_and_not_a_disc():
    """The second half of the original field report — *"Same thing with
    the small green circle when minimized"* — asked of the light's new
    home. The minimized state is the tab itself, and the tab carries a
    stoplight glyph rather than a disc: "let's use a stoplight instead of
    a green inside minimized tab". The worst colour rides the tab's edge,
    so the glance still gets its answer."""
    src = (REPO / "app" / "src" / "WatchLights.tsx").read_text(encoding="utf-8")
    assert "🚦" in src, "the lights' tab lost its stoplight glyph"
    assert "borderColor: COLORS[worstTone]" in src, (
        "the tab no longer wears the worst light's colour — a stoplight "
        "that is the same on a red day and a green one says nothing")
    assert ".wl-dot-face" not in (REPO / "app" / "src" / "styles.css").read_text(
        encoding="utf-8"), "the minimized disc is back in the stylesheet"


def test_the_light_stays_inside_the_glass():
    """A panel wider than the phone pushes the page sideways, which is the
    other way a fixed element takes a screen over."""
    for block in (_base(), _mobile_block()):
        rule = _rule(block, ".edge-panel")
        assert rule and ("max-width" in rule or "width: min(" in rule), (
            "the dock panel has no width limit, so on a narrow phone it can "
            "widen past the viewport and push the page sideways")


def test_the_round_face_opens_from_the_tab_and_is_never_parked():
    """The circle stays — "I still like the circle version as the full
    screen window for running agents" — as the panel the tab opens, not
    as a window pinned to a corner. Pinned is how it came to sit on the
    sidebar's last tabs and the room's record card."""
    src = (REPO / "app" / "src" / "WatchLights.tsx").read_text(encoding="utf-8")
    assert re.search(r"\{open && \(\s*<div className=\{\"edge-panel watch-lights\"", src), (
        "the watch face is drawn without the tab being pressed — a window "
        "that is always up is the corner widget again")
    face = _rule(_base(), ".watch-lights")
    assert face and "border-radius: 50%" in face, (
        "the lights' panel is no longer the round watch face the owner kept")
    assert "position: fixed" not in face, (
        "the watch face is fixed to the glass on its own — it belongs to "
        "the dock and opens beside the tab")


def test_the_round_face_can_say_which_agent():
    """"That way it could be elaborated when necessary on that larger
    window on which particular agent is hung up, running or stopped."
    Each row of the face is a press, and a pressed row names who stands
    under that light from the same payload the wrist reads — the agents
    by goal, the robots by name."""
    src = (REPO / "app" / "src" / "WatchLights.tsx").read_text(encoding="utf-8")
    assert re.search(r'className=\{"wl-row"', src) and "aria-expanded={which === r.tone}" in src, (
        "the rows of the face are no longer presses, so the window cannot "
        "elaborate")
    assert "face.agents" in src and "face.robots" in src, (
        "the elaboration no longer reads the agents and robots off the face")
    api = (REPO / "app" / "src" / "api.ts").read_text(encoding="utf-8")
    assert re.search(r"agents\?: \{ id: string; goal: string;", api), (
        "the WatchFace type no longer carries the agents the route sends")
    grown = _rule(_base(), ".watch-lights.elaborated")
    assert grown and "height: auto" in grown, (
        "the elaborated face cannot grow to hold the names")


def test_the_dock_can_be_moved_and_the_move_is_remembered():
    """The half of the request that is not a stylesheet question: "tabs
    ... that can be moved up or down". A dock that cannot be moved is the
    corner widget again, in a new corner."""
    src = (REPO / "app" / "src" / "EdgeDock.tsx").read_text(encoding="utf-8")
    assert "onPointerDown={down}" in src and "onPointerMove={move}" in src, (
        "the dock's grip no longer follows a pointer")
    assert re.search(r"ArrowUp.*ArrowDown", src), (
        "the grip answers a pointer and not a keyboard")
    assert "localStorage.setItem(Y_KEY" in src, (
        "where the dock was left is forgotten on the next load — a person "
        "who moved it out of the way has to move it again every time")
    grip = _rule(_base(), ".edge-grip")
    assert grip and "touch-action: none" in grip, (
        "the grip has no `touch-action: none`, so on a phone a drag "
        "scrolls the page instead of moving the dock")
