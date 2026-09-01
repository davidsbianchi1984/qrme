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


#: Everything pinned to the bottom of the viewport. A new one is a new row
#: here, which is the point: the question is asked of the class of thing,
#: not of the one that was reported.
BOTTOM_FIXED = (".help-fab", ".help-panel", ".watch-lights", ".wl-dot")


def test_the_stylesheet_still_pins_these_to_the_bottom():
    """The guard on the guard. If the light stopped being fixed — or was
    renamed — every assertion below would pass on an empty reading."""
    css = _base()
    for selector in BOTTOM_FIXED:
        rule = _rule(css, selector)
        assert rule, f"{selector} is not in styles.css any more"
        assert "position: fixed" in rule and _px(rule, "bottom") is not None, (
            f"{selector} is no longer fixed to the bottom of the viewport — "
            "either this list is stale or the light moved, and both want a "
            "person to look")


@pytest.mark.parametrize("selector", BOTTOM_FIXED)
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
                "so an open menu sits under the light — the field report "
                'that produced this guard read "It seems to be blocking '
                'the PDI menus"')


#: What the minimized light may occupy on a phone, and how solid it may be.
#: Both numbers are QRME's, which arrived at them after the same report
#: about the same widget.
DOT_MAX_PX, DOT_MAX_OPACITY = 24.0, 0.9

#: What a thumb has to be able to hit. The blanket
#: `button { min-height: 44px }` in the phone block is where this
#: number comes from, and the dot is a button like any other.
TAP_MIN_PX = 44.0


def test_the_minimized_light_is_a_dot_and_not_a_disc():
    """The second half of the same field report.

    The first photograph showed the light covering the tabs; lifting it
    answered that. The next one — *"Same thing with the small green circle
    when minimized"* — showed the minimized state, and it was not small: a
    40px solid disc with a heavy shadow, sitting over the screen's own
    content at full strength.

        asked     does the minimized light clear the menu
        mattered  is the minimized light small enough to be minimized

    Minimizing is the reader saying *get out of the way*. A widget that
    answers by staying the same size in a different shape has not obeyed;
    it has only stopped explaining itself.
    """
    # The dot is a <button>, and the phone block sets
    # `button { min-height: 44px }` so every control is a real tap target.
    # `min-height` beats `height`, so a 22px square rendered 22 wide and 44
    # tall — an ellipse. This guard read the declared width and height, saw
    # 22 and 22, and passed on it for two releases.
    #
    #     asked     how big is the dot declared
    #     mattered  how big is the dot drawn
    #
    # So there are two elements and two questions. The button is the tap
    # target and may not shrink under 44; the face is the paint and may not
    # grow past a dot. Neither number can be read off the other, which is
    # the whole reason the first version of this could not see the defect.
    target = _rule(_mobile_block(), ".wl-dot")
    assert target, (
        ".wl-dot has no rule at the mobile breakpoint, so it keeps its "
        "desktop size on a phone")
    for prop in ("width", "height"):
        size = _px(target, prop)
        assert size is not None and size >= TAP_MIN_PX, (
            f"the minimized light's tap target is {size}px {prop} on a "
            f"phone, under the {TAP_MIN_PX}px every other control here "
            "gets. The face inside it may be small; the thing a thumb has "
            "to hit may not be")

    rule = _rule(_mobile_block(), ".wl-dot-face")
    assert rule, (
        ".wl-dot-face has no rule at the mobile breakpoint, so the dot keeps "
        "its desktop size on a phone")
    for prop in ("width", "height"):
        size = _px(rule, prop)
        assert size is not None and size <= DOT_MAX_PX, (
            f"the minimized light's {prop} is {size}px on a phone; a dot "
            f"that is more than {DOT_MAX_PX}px is a disc parked on the "
            "content")
    m = re.search(r"\bopacity:\s*([\d.]+)\s*;", rule)
    assert m and float(m.group(1)) <= DOT_MAX_OPACITY, (
        "the minimized light is fully opaque on a phone — it hides whatever "
        "is under it rather than sitting lightly over it")


def test_the_light_stays_inside_the_glass():
    """A panel wider than the phone pushes the page sideways, which is the
    other way a fixed element takes a screen over."""
    rule = _rule(_base(), ".help-panel")
    assert rule and ("max-width" in rule or "width: min(" in rule), (
        "the help panel has no width limit, so on a narrow phone it can "
        "widen past the viewport and push the page sideways")
