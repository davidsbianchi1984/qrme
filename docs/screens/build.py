#!/usr/bin/env python3
"""Generate the QRME app-screen SVGs — one static, full-colour screen per
capability, in the product's deep-indigo / neon-purple style. Every screen is
self-contained SVG (no fonts, images, or scripts), so it renders identically in
a browser, a README, and any converter.

Run:    python3 docs/screens/build.py
Output: docs/screens/NN-name.svg
Design language: Deep Indigo #1A1333 · Neon Purple #7B5CFF · Warm Amber #FFB84D
                 · Soft Silver #C7C9D9 · SF-style system type · liquid-glass cards.
"""

from __future__ import annotations

import html
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frames          # generated: tools/encode_desk_frames.py
import textwidth as tw  # generated: tools/measure_text.py

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- palette (QRME design language) ---------------------------------------
C = {
    "scrA": "#181235", "scrB": "#0c0920", "frameA": "#2a2352", "frameB": "#0a0818",
    "card": "#201a48", "card2": "#181240", "line": "#302a60", "tab": "#0e0a26",
    "txt": "#f2effc", "t2": "#9a93c6", "t3": "#6a6399",
    "brandA": "#7b5cff", "brandB": "#9d7bff",          # neon purple
    "amber": "#ffb84d", "green": "#7bc47f", "cyan": "#9fd8e8",
    "red": "#e0687a", "gold": "#ffce54", "silver": "#c7c9d9", "pink": "#e78bd0",
    "indigo": "#5b54d6",
}
ACCENT = {"brand": C["brandA"], "amber": C["amber"], "green": C["green"],
          "cyan": C["cyan"], "red": C["red"], "gold": C["gold"],
          "silver": C["silver"], "pink": C["pink"], "indigo": C["indigo"]}
FONT = ("-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text',"
        "'Segoe UI',Roboto,system-ui,sans-serif")

W, H = 320, 660
PX, PY, PW, PH = 10, 12, 300, 636
SX, SY, SW, SH = 20, 22, 280, 616
CX, CW = 34, 252            # content left / width


def esc(s):
    return html.escape(str(s), quote=True)


def A(hexcol, a):
    """hex #rrggbb + alpha 0..1 -> rgba() string. cairosvg-safe (8-digit hex
    alpha renders opaque there; rgba() is honoured everywhere)."""
    h = hexcol.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


# --------------------------------------------------------------------------- #
# tiny vector icon set (drawn, not emoji, so it renders identically anywhere)
# --------------------------------------------------------------------------- #
def icon(name, cx, cy, col, s=1.0):
    def sc(v):
        return v * s
    p = f'fill="{col}"'
    st = f'fill="none" stroke="{col}" stroke-width="{1.7*s:.2f}" stroke-linecap="round" stroke-linejoin="round"'
    if name == "person":
        return (f'<circle cx="{cx}" cy="{cy-sc(4)}" r="{sc(3.6)}" {st}/>'
                f'<path d="M{cx-sc(6)} {cy+sc(7)} c0 -{sc(6)} {sc(12)} -{sc(6)} {sc(12)} 0" {st}/>')
    if name == "addphoto":
        # The same mark as qrme/assets/figures/add-photo.svg: a picture frame
        # with a plus badged on. Drawn here too so the screen shows the control
        # rather than a word describing it.
        return (f'<rect x="{cx-sc(9)}" y="{cy-sc(7.5)}" width="{sc(15)}" '
                f'height="{sc(12)}" rx="{sc(2.4)}" {st}/>'
                f'<circle cx="{cx-sc(4.6)}" cy="{cy-sc(3.4)}" r="{sc(1.5)}" '
                f'{p}/>'
                f'<path d="M{cx-sc(8)} {cy+sc(3.4)} L{cx-sc(2.6)} '
                f'{cy-sc(1.4)} L{cx+sc(1.4)} {cy+sc(2.2)}" {st}/>'
                f'<circle cx="{cx+sc(6.4)}" cy="{cy+sc(6)}" r="{sc(4.6)}" '
                f'{p}/>'
                f'<path d="M{cx+sc(6.4)} {cy+sc(3.6)} V{cy+sc(8.4)} '
                f'M{cx+sc(4)} {cy+sc(6)} H{cx+sc(8.8)}" fill="none" '
                f'stroke="#0d0a20" stroke-width="{1.6*s:.2f}" '
                f'stroke-linecap="round"/>')
    if name == "people":
        return (f'<circle cx="{cx-sc(4)}" cy="{cy-sc(4)}" r="{sc(3)}" {st}/>'
                f'<circle cx="{cx+sc(4)}" cy="{cy-sc(4)}" r="{sc(3)}" {st}/>'
                f'<path d="M{cx-sc(9)} {cy+sc(6)} c0 -{sc(5)} {sc(6)} -{sc(5)} {sc(6)} 0 M{cx-sc(1)} {cy+sc(6)} c0 -{sc(5)} {sc(7)} -{sc(5)} {sc(9)} -{sc(1)}" {st}/>')
    if name == "mask":
        return (f'<path d="M{cx-sc(8)} {cy-sc(5)} c{sc(4)} -{sc(2)} {sc(12)} -{sc(2)} {sc(16)} 0 '
                f'c0 {sc(8)} -{sc(5)} {sc(11)} -{sc(8)} {sc(11)} c-{sc(3)} 0 -{sc(8)} -{sc(3)} -{sc(8)} -{sc(11)} Z" {st}/>'
                f'<circle cx="{cx-sc(3)}" cy="{cy-sc(1)}" r="{sc(1)}" {p}/><circle cx="{cx+sc(3)}" cy="{cy-sc(1)}" r="{sc(1)}" {p}/>')
    if name == "star2":  # creator persona
        return (f'<path d="M{cx} {cy-sc(8)} l{sc(2.4)} {sc(5)} {sc(5.4)} {sc(0.6)} -{sc(4)} {sc(3.8)} {sc(1.1)} {sc(5.3)} '
                f'-{sc(4.9)} -{sc(2.7)} -{sc(4.9)} {sc(2.7)} {sc(1.1)} -{sc(5.3)} -{sc(4)} -{sc(3.8)} {sc(5.4)} -{sc(0.6)} Z" {st}/>')
    if name == "building":
        return (f'<rect x="{cx-sc(6)}" y="{cy-sc(8)}" width="{sc(12)}" height="{sc(16)}" rx="1.5" {st}/>'
                + "".join(f'<rect x="{cx-sc(4)+j*sc(3)}" y="{cy-sc(5)+i*sc(3.4)}" width="{sc(2)}" height="{sc(2)}" rx="0.4" {p}/>'
                          for i in range(3) for j in range(3)))
    if name == "photo":
        return (f'<rect x="{cx-sc(8)}" y="{cy-sc(6)}" width="{sc(16)}" height="{sc(12)}" rx="2" {st}/>'
                f'<circle cx="{cx-sc(3)}" cy="{cy-sc(1)}" r="{sc(1.8)}" {st}/>'
                f'<path d="M{cx-sc(8)} {cy+sc(4)} l{sc(5)} -{sc(4)} {sc(4)} {sc(3)} {sc(3)} -{sc(2)} {sc(4)} {sc(3)}" {st}/>')
    if name == "pen":
        return (f'<path d="M{cx-sc(7)} {cy+sc(7)} l{sc(2)} -{sc(5)} {sc(9)} -{sc(9)} {sc(3)} {sc(3)} -{sc(9)} {sc(9)} -{sc(5)} {sc(2)} Z" {st}/>'
                f'<path d="M{cx+sc(2)} {cy-sc(6)} l{sc(3)} {sc(3)}" {st}/>')
    if name == "cal":
        return (f'<rect x="{cx-sc(7)}" y="{cy-sc(6)}" width="{sc(14)}" height="{sc(13)}" rx="2" {st}/>'
                f'<path d="M{cx-sc(7)} {cy-sc(2)} h{sc(14)} M{cx-sc(3)} {cy-sc(8)} v{sc(3)} M{cx+sc(3)} {cy-sc(8)} v{sc(3)}" {st}/>')
    if name == "db":
        return (f'<ellipse cx="{cx}" cy="{cy-sc(5)}" rx="{sc(7)}" ry="{sc(2.6)}" {st}/>'
                f'<path d="M{cx-sc(7)} {cy-sc(5)} v{sc(10)} c0 {sc(1.5)} {sc(3)} {sc(2.6)} {sc(7)} {sc(2.6)} '
                f's{sc(7)} -{sc(1.1)} {sc(7)} -{sc(2.6)} v-{sc(10)} M{cx-sc(7)} {cy} c0 {sc(1.5)} {sc(3)} {sc(2.6)} {sc(7)} {sc(2.6)} s{sc(7)} -{sc(1.1)} {sc(7)} -{sc(2.6)}" {st}/>')
    if name == "mic":
        return (f'<rect x="{cx-sc(3)}" y="{cy-sc(8)}" width="{sc(6)}" height="{sc(11)}" rx="{sc(3)}" {st}/>'
                f'<path d="M{cx-sc(6)} {cy} c0 {sc(5)} {sc(12)} {sc(5)} {sc(12)} 0 M{cx} {cy+sc(5)} v{sc(3)}" {st}/>')
    if name == "chat":
        return f'<path d="M{cx-sc(8)} {cy-sc(6)} h{sc(16)} a2 2 0 0 1 2 2 v{sc(7)} a2 2 0 0 1 -2 2 h-{sc(9)} l-{sc(4)} {sc(4)} v-{sc(4)} h-{sc(3)} a2 2 0 0 1 -2 -2 v-{sc(7)} a2 2 0 0 1 2 -2 Z" {st}/>'
    if name == "heart":
        return (f'<path d="M{cx} {cy+sc(6)} C{cx-sc(9)} {cy-sc(3)},{cx-sc(7)} {cy-sc(9)},{cx} {cy-sc(4)} '
                f'C{cx+sc(7)} {cy-sc(9)},{cx+sc(9)} {cy-sc(3)},{cx} {cy+sc(6)} Z" {p}/>')
    if name == "lock":
        return (f'<rect x="{cx-sc(6)}" y="{cy-sc(2)}" width="{sc(12)}" height="{sc(9)}" rx="2" {st}/>'
                f'<path d="M{cx-sc(3.5)} {cy-sc(2)} v-{sc(3)} a{sc(3.5)} {sc(3.5)} 0 0 1 {sc(7)} 0 v{sc(3)}" {st}/>'
                f'<circle cx="{cx}" cy="{cy+sc(2.5)}" r="{sc(1.2)}" {p}/>')
    if name == "shield":
        return f'<path d="M{cx} {cy-sc(8)} l{sc(7)} {sc(3)} v{sc(5)} c0 {sc(5)} -{sc(3)} {sc(7)} -{sc(7)} {sc(9)} c-{sc(4)} -{sc(2)} -{sc(7)} -{sc(4)} -{sc(7)} -{sc(9)} v-{sc(5)} Z" {st}/>'
    if name == "shieldok":
        return (f'<path d="M{cx} {cy-sc(8)} l{sc(7)} {sc(3)} v{sc(5)} c0 {sc(5)} -{sc(3)} {sc(7)} -{sc(7)} {sc(9)} c-{sc(4)} -{sc(2)} -{sc(7)} -{sc(4)} -{sc(7)} -{sc(9)} v-{sc(5)} Z" {st}/>'
                f'<path d="M{cx-sc(3)} {cy} l{sc(2)} {sc(2.4)} {sc(4)} -{sc(4.5)}" {st}/>')
    if name == "eye":
        return (f'<path d="M{cx-sc(8)} {cy} c{sc(4)} -{sc(6)} {sc(12)} -{sc(6)} {sc(16)} 0 c-{sc(4)} {sc(6)} -{sc(12)} {sc(6)} -{sc(16)} 0 Z" {st}/>'
                f'<circle cx="{cx}" cy="{cy}" r="{sc(2.4)}" {p}/>')
    if name == "chart":
        return "".join(f'<rect x="{cx-sc(7)+i*sc(5)}" y="{cy+sc(6)-sc([5,9,4,11][i])}" width="{sc(3.2)}" height="{sc([5,9,4,11][i])}" rx="1" {p}/>' for i in range(4))
    if name == "gear":
        teeth = "".join(f'<rect x="{cx-sc(1.3)}" y="{cy-sc(9)}" width="{sc(2.6)}" height="{sc(4)}" rx="1" transform="rotate({a} {cx} {cy})" {p}/>' for a in range(0, 360, 45))
        return teeth + f'<circle cx="{cx}" cy="{cy}" r="{sc(4.6)}" {st}/>'
    if name == "target":
        return (f'<circle cx="{cx}" cy="{cy}" r="{sc(7.5)}" {st}/>'
                f'<circle cx="{cx}" cy="{cy}" r="{sc(3.5)}" {st}/>'
                f'<circle cx="{cx}" cy="{cy}" r="{sc(0.9)}" {p}/>')
    if name == "search":
        return (f'<circle cx="{cx-sc(2)}" cy="{cy-sc(2)}" r="{sc(6)}" {st}/>'
                f'<path d="M{cx+sc(3)} {cy+sc(3)} l{sc(4)} {sc(4)}" {st}/>')
    if name == "clock":
        return (f'<circle cx="{cx}" cy="{cy}" r="{sc(7.5)}" {st}/>'
                f'<path d="M{cx} {cy-sc(4)} v{sc(4)} l{sc(3)} {sc(2)}" {st}/>')
    if name == "grid":
        return "".join(f'<rect x="{cx-sc(7)+j*sc(8)}" y="{cy-sc(7)+i*sc(8)}" width="{sc(6)}" height="{sc(6)}" rx="1.4" {st}/>' for i in range(2) for j in range(2))
    if name == "list":
        return (f'<path d="M{cx-sc(6)} {cy-sc(5)} h{sc(12)} M{cx-sc(6)} {cy} h{sc(12)} M{cx-sc(6)} {cy+sc(5)} h{sc(12)}" {st}/>')
    if name == "doc":
        return (f'<path d="M{cx-sc(6)} {cy-sc(8)} h{sc(8)} l{sc(4)} {sc(4)} v{sc(12)} h-{sc(12)} Z" {st}/>'
                f'<path d="M{cx-sc(3)} {cy-sc(1)} h{sc(6)} M{cx-sc(3)} {cy+sc(3)} h{sc(6)}" {st}/>')
    if name == "coin":
        return (f'<circle cx="{cx}" cy="{cy}" r="{sc(7.5)}" {st}/>'
                f'<path d="M{cx} {cy-sc(4)} v{sc(8)} M{cx-sc(2.4)} {cy-sc(2)} h{sc(4)} a{sc(2)} {sc(2)} 0 0 1 0 {sc(4)} h-{sc(4.8)}" {st}/>')
    if name == "gift":
        return (f'<rect x="{cx-sc(7)}" y="{cy-sc(3)}" width="{sc(14)}" height="{sc(9)}" rx="1.5" {st}/>'
                f'<path d="M{cx-sc(8)} {cy-sc(3)} h{sc(16)} M{cx} {cy-sc(3)} v{sc(9)} '
                f'M{cx} {cy-sc(3)} c-{sc(4)} 0 -{sc(5)} -{sc(5)} 0 -{sc(4)} c{sc(4)} -{sc(1)} {sc(4)} {sc(4)} 0 {sc(4)}" {st}/>')
    if name == "info":
        return (f'<circle cx="{cx}" cy="{cy}" r="{sc(7.5)}" {st}/>'
                f'<circle cx="{cx}" cy="{cy-sc(3.5)}" r="{sc(0.9)}" {p}/><path d="M{cx} {cy-sc(1)} v{sc(4.5)}" {st}/>')
    if name == "compass":
        return (f'<circle cx="{cx}" cy="{cy}" r="{sc(7.5)}" {st}/>'
                f'<path d="M{cx+sc(3.5)} {cy-sc(3.5)} l-{sc(2.2)} {sc(5)} -{sc(5)} {sc(2.2)} {sc(2.2)} -{sc(5)} Z" {p}/>')
    if name == "net":
        return (f'<circle cx="{cx}" cy="{cy-sc(5)}" r="{sc(2.4)}" {st}/>'
                f'<circle cx="{cx-sc(6)}" cy="{cy+sc(4)}" r="{sc(2.4)}" {st}/>'
                f'<circle cx="{cx+sc(6)}" cy="{cy+sc(4)}" r="{sc(2.4)}" {st}/>'
                f'<path d="M{cx} {cy-sc(3)} l-{sc(5)} {sc(6)} M{cx} {cy-sc(3)} l{sc(5)} {sc(6)} M{cx-sc(4)} {cy+sc(4)} h{sc(8)}" {st}/>')
    if name == "sliders":
        return (f'<path d="M{cx-sc(7)} {cy-sc(5)} h{sc(14)} M{cx-sc(7)} {cy} h{sc(14)} M{cx-sc(7)} {cy+sc(5)} h{sc(14)}" {st}/>'
                f'<circle cx="{cx+sc(2)}" cy="{cy-sc(5)}" r="{sc(2)}" {p}/><circle cx="{cx-sc(3)}" cy="{cy}" r="{sc(2)}" {p}/><circle cx="{cx+sc(4)}" cy="{cy+sc(5)}" r="{sc(2)}" {p}/>')
    if name == "watch":
        return (f'<rect x="{cx-sc(5)}" y="{cy-sc(5)}" width="{sc(10)}" height="{sc(10)}" rx="2.5" {st}/>'
                f'<path d="M{cx-sc(2.5)} {cy-sc(5)} v-{sc(3)} h{sc(5)} v{sc(3)} M{cx-sc(2.5)} {cy+sc(5)} v{sc(3)} h{sc(5)} v-{sc(3)}" {st}/>')
    if name == "phone":
        return (f'<rect x="{cx-sc(5)}" y="{cy-sc(8)}" width="{sc(10)}" height="{sc(16)}" rx="2.4" {st}/>'
                f'<path d="M{cx-sc(1.6)} {cy+sc(5)} h{sc(3.2)}" {st}/>')
    if name == "headset":
        return (f'<path d="M{cx-sc(8)} {cy+sc(1)} v-{sc(1)} a{sc(8)} {sc(8)} 0 0 1 {sc(16)} 0 v{sc(1)}" {st}/>'
                f'<rect x="{cx-sc(9)}" y="{cy+sc(1)}" width="{sc(4)}" height="{sc(7)}" rx="1.6" {st}/>'
                f'<rect x="{cx+sc(5)}" y="{cy+sc(1)}" width="{sc(4)}" height="{sc(7)}" rx="1.6" {st}/>')
    if name == "robot":
        return (f'<rect x="{cx-sc(7)}" y="{cy-sc(4)}" width="{sc(14)}" height="{sc(11)}" rx="3" {st}/>'
                f'<path d="M{cx} {cy-sc(4)} v-{sc(3)}" {st}/><circle cx="{cx}" cy="{cy-sc(8)}" r="{sc(1.4)}" {p}/>'
                f'<circle cx="{cx-sc(3)}" cy="{cy+sc(1)}" r="{sc(1.5)}" {p}/><circle cx="{cx+sc(3)}" cy="{cy+sc(1)}" r="{sc(1.5)}" {p}/>')
    if name == "speaker":
        return (f'<rect x="{cx-sc(6)}" y="{cy-sc(8)}" width="{sc(12)}" height="{sc(16)}" rx="3" {st}/>'
                f'<circle cx="{cx}" cy="{cy+sc(2)}" r="{sc(3.4)}" {st}/><circle cx="{cx}" cy="{cy-sc(5)}" r="{sc(1)}" {p}/>')
    if name == "cloud":
        return f'<path d="M{cx-sc(6)} {cy+sc(4)} a{sc(4)} {sc(4)} 0 0 1 {sc(1)} -{sc(8)} a{sc(5)} {sc(5)} 0 0 1 {sc(10)} {sc(1)} a{sc(3.5)} {sc(3.5)} 0 0 1 -{sc(1)} {sc(7)} Z" {st}/>'
    if name == "finger":
        return (f'<path d="M{cx-sc(6)} {cy+sc(2)} c0 -{sc(7)} {sc(3)} -{sc(9)} {sc(6)} -{sc(9)} c{sc(3)} 0 {sc(6)} {sc(2)} {sc(6)} {sc(7)}" {st}/>'
                f'<path d="M{cx-sc(3)} {cy+sc(4)} c0 -{sc(6)} {sc(2)} -{sc(7)} {sc(3)} -{sc(7)} c{sc(2)} 0 {sc(3)} {sc(2)} {sc(3)} {sc(5)}" {st}/>'
                f'<path d="M{cx} {cy+sc(6)} v-{sc(6)}" {st}/>')
    if name == "brain":
        return (f'<circle cx="{cx-sc(3)}" cy="{cy}" r="{sc(5)}" {st}/>'
                f'<circle cx="{cx+sc(3)}" cy="{cy}" r="{sc(5)}" {st}/>')
    if name == "bolt":
        return f'<path d="M{cx+sc(2)} {cy-sc(8)} L{cx-sc(6)} {cy+sc(1)} L{cx} {cy+sc(1)} L{cx-sc(2)} {cy+sc(8)} L{cx+sc(6)} {cy-sc(1)} L{cx} {cy-sc(1)} Z" {p}/>'
    if name == "leaf":
        return f'<path d="M{cx-sc(6)} {cy+sc(6)} c0 -{sc(9)} {sc(6)} -{sc(13)} {sc(12)} -{sc(12)} c{sc(1)} {sc(6)} -{sc(3)} {sc(12)} -{sc(12)} {sc(12)} Z M{cx-sc(3)} {cy+sc(3)} l{sc(6)} -{sc(6)}" {st}/>'
    if name == "link":
        return f'<path d="M{cx-sc(2)} {cy+sc(2)} l-{sc(3)} {sc(3)} a{sc(3)} {sc(3)} 0 0 1 -{sc(4)} -{sc(4)} l{sc(3)} -{sc(3)} m{sc(6)} -{sc(2)} l{sc(3)} -{sc(3)} a{sc(3)} {sc(3)} 0 0 1 {sc(4)} {sc(4)} l-{sc(3)} {sc(3)} M{cx-sc(3)} {cy+sc(3)} l{sc(6)} -{sc(6)}" {st}/>'
    if name == "warn":
        return (f'<path d="M{cx} {cy-sc(8)} L{cx+sc(8)} {cy+sc(6)} H{cx-sc(8)} Z" {st}/>'
                f'<path d="M{cx} {cy-sc(3)} v{sc(4)}" {st}/><circle cx="{cx}" cy="{cy+sc(4)}" r="{sc(0.9)}" {p}/>')
    if name == "plus":
        return f'<path d="M{cx} {cy-sc(7)} v{sc(14)} M{cx-sc(7)} {cy} h{sc(14)}" fill="none" stroke="{col}" stroke-width="{2.4*s:.2f}" stroke-linecap="round"/>'
    if name == "cross":  # medical
        return f'<path d="M{cx} {cy-sc(7)} v{sc(14)} M{cx-sc(7)} {cy} h{sc(14)}" fill="none" stroke="{col}" stroke-width="{3*s:.2f}" stroke-linecap="round"/>'
    if name == "book":
        return (f'<rect x="{cx-sc(7)}" y="{cy-sc(7)}" width="{sc(14)}" height="{sc(14)}" rx="2" {st}/>'
                f'<path d="M{cx} {cy-sc(7)} v{sc(14)}" {st}/>')
    if name == "flag":
        return (f'<path d="M{cx-sc(6)} {cy+sc(8)} v-{sc(16)}" {st}/>'
                f'<path d="M{cx-sc(6)} {cy-sc(7)} h{sc(11)} l-{sc(2.5)} {sc(3.5)} {sc(2.5)} {sc(3.5)} h-{sc(11)} Z" {st}/>')
    if name == "expand":  # go full screen — corners pushing out
        return (f'<path d="M{cx+sc(2)} {cy-sc(7)} H{cx+sc(7)} V{cy-sc(2)} '
                f'M{cx+sc(7)} {cy-sc(7)} L{cx+sc(1)} {cy-sc(1)}" {st}/>'
                f'<path d="M{cx-sc(2)} {cy+sc(7)} H{cx-sc(7)} V{cy+sc(2)} '
                f'M{cx-sc(7)} {cy+sc(7)} L{cx-sc(1)} {cy+sc(1)}" {st}/>')
    if name == "shrink":  # and back out of it — corners pulling in
        return (f'<path d="M{cx+sc(7)} {cy-sc(2)} H{cx+sc(2)} V{cy-sc(7)} '
                f'M{cx+sc(2)} {cy-sc(2)} L{cx+sc(7)} {cy-sc(7)}" {st}/>'
                f'<path d="M{cx-sc(7)} {cy+sc(2)} H{cx-sc(2)} V{cy+sc(7)} '
                f'M{cx-sc(2)} {cy+sc(2)} L{cx-sc(7)} {cy+sc(7)}" {st}/>')
    if name == "rotate":  # tilt the phone — the way into landscape
        # Two phones and the turn between them. A single tilted phone with a
        # curved arrow is the usual glyph and it is illegible at 15px; the
        # before-and-after reads instantly at any size because the shapes
        # differ rather than the annotation.
        return (f'<rect x="{cx-sc(8.5)}" y="{cy-sc(6)}" width="{sc(6.5)}" '
                f'height="{sc(11)}" rx="1.6" {st}/>'
                f'<rect x="{cx+sc(1)}" y="{cy-sc(3.2)}" width="{sc(11)}" '
                f'height="{sc(6.5)}" rx="1.6" {st}/>'
                f'<path d="M{cx-sc(1)} {cy-sc(6.5)} a{sc(6)} {sc(6)} 0 0 1 {sc(3.4)} -{sc(1.6)}" {st}/>'
                f'<path d="M{cx+sc(0.6)} {cy-sc(9.6)} l-{sc(1.8)} {sc(2.6)} {sc(2.8)} {sc(1)}" {st}/>')
    if name == "smiley":  # the emoji key inside a composer
        return (f'<circle cx="{cx}" cy="{cy}" r="{sc(7)}" {st}/>'
                f'<circle cx="{cx-sc(2.6)}" cy="{cy-sc(2)}" r="{sc(1.1)}" {p}/>'
                f'<circle cx="{cx+sc(2.6)}" cy="{cy-sc(2)}" r="{sc(1.1)}" {p}/>'
                f'<path d="M{cx-sc(3.4)} {cy+sc(2)} a{sc(3.6)} {sc(3.6)} 0 0 0 {sc(6.8)} 0" {st}/>')
    if name == "bell":  # ring the bell on a desk
        return (f'<path d="M{cx-sc(7)} {cy+sc(4)} C{cx-sc(5.5)} {cy+sc(1)} {cx-sc(5)} {cy-sc(2)} {cx-sc(5)} {cy-sc(4)} '
                f'A{sc(5)} {sc(5)} 0 0 1 {cx+sc(5)} {cy-sc(4)} '
                f'C{cx+sc(5)} {cy-sc(2)} {cx+sc(5.5)} {cy+sc(1)} {cx+sc(7)} {cy+sc(4)} Z" {st}/>'
                f'<path d="M{cx-sc(2.2)} {cy+sc(4)} a{sc(2.2)} {sc(2.2)} 0 0 0 {sc(4.4)} 0" {st}/>'
                f'<circle cx="{cx}" cy="{cy-sc(8.6)}" r="{sc(1.2)}" {p}/>')
    if name == "share":  # pass it on — three nodes, two edges
        return (f'<circle cx="{cx+sc(5)}" cy="{cy-sc(6)}" r="{sc(2.6)}" {st}/>'
                f'<circle cx="{cx-sc(6)}" cy="{cy}" r="{sc(2.6)}" {st}/>'
                f'<circle cx="{cx+sc(5)}" cy="{cy+sc(6)}" r="{sc(2.6)}" {st}/>'
                f'<path d="M{cx-sc(3.6)} {cy-sc(1.2)} l{sc(6.2)} -{sc(3.6)} '
                f'M{cx-sc(3.6)} {cy+sc(1.2)} l{sc(6.2)} {sc(3.6)}" {st}/>')
    if name == "comeup":  # ask to come up as a guest — a person, and up
        return (f'<circle cx="{cx-sc(3)}" cy="{cy-sc(4)}" r="{sc(3.2)}" {st}/>'
                f'<path d="M{cx-sc(9)} {cy+sc(7)} c0 -{sc(5.4)} {sc(12)} -{sc(5.4)} {sc(12)} 0" {st}/>'
                f'<path d="M{cx+sc(6)} {cy+sc(3)} v-{sc(9)} '
                f'M{cx+sc(2.8)} {cy-sc(2.8)} l{sc(3.2)} -{sc(3.2)} {sc(3.2)} {sc(3.2)}" {st}/>')
    if name == "dove":  # memorial / departure
        return (f'<path d="M{cx-sc(8)} {cy+sc(2)} c{sc(3)} -{sc(5)} {sc(8)} -{sc(6)} {sc(11)} -{sc(3)} '
                f'c{sc(2)} -{sc(4)} {sc(5)} -{sc(4)} {sc(5)} -{sc(4)} c-{sc(1)} {sc(3)} -{sc(2)} {sc(4)} -{sc(4)} {sc(5)} '
                f'c-{sc(1)} {sc(4)} -{sc(5)} {sc(6)} -{sc(9)} {sc(5)} l{sc(2)} {sc(3)} h-{sc(5)} Z" {st}/>')
    # fallback dot
    return f'<circle cx="{cx}" cy="{cy}" r="{sc(4)}" {p}/>'


def stars(x, y, rating, col, s=1.0):
    """Row of 5 stars, `rating` (0..5) filled; returns svg + label handled by caller."""
    out = []
    for i in range(5):
        cx = x + i * 12 * s
        full = i < math.floor(rating)
        fill = col if full else "none"
        out.append(f'<path d="M{cx} {y-4*s} l{1.3*s} {2.7*s} {2.9*s} {0.3*s} -{2.1*s} {2*s} {0.6*s} {2.9*s} '
                   f'-{2.6*s} -{1.5*s} -{2.6*s} {1.5*s} {0.6*s} -{2.9*s} -{2.1*s} -{2*s} {2.9*s} -{0.3*s} Z" '
                   f'fill="{fill}" stroke="{col}" stroke-width="{0.9*s}" stroke-linejoin="round"/>')
    return "".join(out)


# --------------------------------------------------------------------------- #
# primitives
# --------------------------------------------------------------------------- #
def rrect(x, y, w, h, r, fill, stroke=None, sw=1):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}"{s}/>'


def text(x, y, s, size, fill, weight=400, anchor="start", spacing=0, mono=False):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    fam = "ui-monospace,Menlo,monospace" if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{ls}>{esc(s)}</text>')


def chip(x, y, ic, col):
    return (rrect(x, y, 34, 34, 11, A(col, 0.16)) + icon(ic, x + 17, y + 17, col, 0.92))


def pill(x, y, label, tone):
    col = {"good": C["green"], "warn": C["amber"], "crit": C["red"],
           "info": C["cyan"], "brand": C["brandA"], "gold": C["gold"]}[tone]
    w = 12 + len(label) * 6.2
    return (rrect(x - w, y - 11, w, 17, 8, A(col, 0.16))
            + text(x - w / 2, y + 1, label, 9.5, col, 700, "middle", 0.4))


def agent_light(x, y, colour, label):
    """The agent status light — green working, amber needs you, red stopped.

    A dot with a soft halo and a word. The word is not decoration: a colour
    alone cannot say whether a green agent is mid-task or finished, and on a
    small screen the word is doing most of the reading anyway. Mapped from the
    workflow status by `qrme/agentlight.py`, which is the only place the
    meaning lives.
    """
    col = {"green": C["green"], "amber": C["amber"], "red": C["red"]}[colour]
    return (f'<circle cx="{x}" cy="{y}" r="10" fill="{A(col, 0.16)}"/>'
            + f'<circle cx="{x}" cy="{y}" r="4.6" fill="{col}"/>'
            + text(x + 15, y + 4, label, 10.5, col, 700, spacing=0.2))


def bubble_chat(x, y, w, rows):
    """The chat overlay in a live room: circular faces on transparent glass.

    Drawn over the video rather than in a panel beside it. A comment strip with
    its own solid background takes a bite out of the picture people came to
    watch; this floats, so the room stays the thing on screen.

    The screens draw their own circles rather than using the baked bubbles in
    ``docs/portraits/bubbles/``. Those exist for the README, which cannot draw
    one — GitHub strips the `style` that would round an `<img>`. Inside the
    product a surface can round its own, and using the pre-baked file here
    would put a bubble inside a bubble.
    """
    out, yy = [], y
    for name, said, b64 in rows:
        # No plate behind the row — just a soft scrim under the text so it
        # survives a bright frame without boxing the video in.
        out.append(f'<circle cx="{x+15}" cy="{yy+13}" r="16" '
                   f'fill="rgba(8,6,22,0.7)"/>')
        out.append(face(x + 15, yy + 13, 26, b64, radius=13))
        out.append(rrect(x + 32, yy + 2, w - 32, 23, 11,
                         "rgba(8,6,22,0.62)"))
        out.append(text(x + 41, yy + 11, name, 8, C["cyan"], 800))
        out.append(text(x + 41, yy + 21, said, 9, "rgba(255,255,255,0.92)",
                        500))
        yy += 30
    return out, yy


D_BTN = 22          # the round buttons on the live bar
G_BTN = 4           # and the gap between them

# A photo that *is* the screen: from where content starts down to just above
# the tab bar. A live room laid out any other way puts the thing somebody came
# to watch in a box with furniture around it.
PHOTO_FULL = (SY + SH - 52) - (SY + 100) - 10


def live_bar(x, y, w, h, actions, placeholder="Type…"):
    """The composer and the reaction buttons, on one line at the foot of a live
    room.

    Every verb here already existed as a route — ``POST /desks/{id}/bell``,
    ``POST /desks/{id}/guests``, ``POST /{kind}/{id}/gift`` and the audience
    layer's like and share — and none of them existed anywhere a thumb could
    reach. A capability with no control is indistinguishable from a missing
    feature, which is exactly how it read.

    The first version of this row was five large labelled buttons under the
    video, and it was wrong twice over: it ate the picture, and it explained
    itself at a size nobody needs. Every live product converges on the same
    answer because it is the right one — the video is the screen, and the
    controls are a single strip at the bottom, small enough to stay out of the
    way and thumb-reachable because that is where the thumb already is.

    So: a composer on the left, then the reactions as small circles pushed to
    the right corner. No captions. An icon at this size has to carry its own
    meaning, which is why the bell is a bell and the guest request is a person
    with an arrow over them rather than anything cleverer.

    Ringing and asking to come up sit in the same strip as like, gift and
    share because from the viewer's side they are one gesture — a thing you do
    to the room you are watching. That the last one needs the host to say yes
    is the host's business, not a reason to file it under a different menu.
    """
    o = []
    right = x + w - 8
    strip = len(actions) * D_BTN + (len(actions) - 1) * G_BTN
    by = y + h - 10 - D_BTN                 # top of the row
    cy = by + D_BTN / 2

    # The composer takes whatever the buttons leave. It has a floor: below
    # this the placeholder is unreadable and the field stops looking like
    # somewhere you can type, which is the only job it has on a still image.
    # Capped as well as floored. On a landscape screen the composer would
    # otherwise run half a metre of glass to reach the buttons, and a text
    # field that wide reads as a banner rather than somewhere to type.
    room = (right - strip - 8) - (x + 8)
    if room < 74:
        raise ValueError(
            f"{len(actions)} buttons leave {room:.0f}px for the composer; "
            f"74 is the floor")
    bar_w = min(room, 240)
    o.append(rrect(x + 8, by, bar_w, D_BTN, D_BTN / 2, "rgba(8,6,22,0.62)",
                   "rgba(255,255,255,0.12)", 1))
    o.append(text(x + 18, cy + 3, placeholder, 8.6,
                  "rgba(232,228,255,0.55)", 500))
    # The emoji key sits inside the right end of the field, where every
    # composer puts it — reactions are one line up, this is for the message.
    o.append(f'<circle cx="{x+8+bar_w-13}" cy="{cy}" r="7.4" '
             f'fill="rgba(255,255,255,0.20)"/>')
    o.append(icon("smiley", x + 8 + bar_w - 13, cy, "rgba(255,255,255,0.82)",
                  0.42))

    bx = right - strip
    for entry in actions:
        ic, col = entry[0], entry[1]
        count = entry[2] if len(entry) > 2 else None
        o.append(f'<circle cx="{bx+D_BTN/2}" cy="{cy}" r="{D_BTN/2}" '
                 f'fill="rgba(8,6,22,0.62)" '
                 f'stroke="{A(ACCENT[col], 0.45)}" stroke-width="0.9"/>')
        o.append(icon(ic, bx + D_BTN / 2, cy, ACCENT[col], 0.44))
        if count:
            # Tucked under the glyph rather than beside it — a count that
            # widens the button breaks the even spacing of the strip.
            o.append(text(bx + D_BTN - 2, cy + D_BTN / 2 - 1, count, 6.4,
                          "rgba(255,255,255,0.85)", 700, "end"))
        bx += D_BTN + G_BTN
    return o, D_BTN + 18


def friends_list(y, entries):
    """A profile's friends, founder first.

    The founder's row carries a small badge saying so. Position alone would
    leave a reader to infer why one face is always at the top, and the honest
    answer — *this one comes as standard, and it cannot be removed* — is short
    enough to just say.
    """
    out, yy = [], y
    for entry in entries:
        name, sub, b64, badge = entry[:4]
        packs = entry[4] if len(entry) > 4 else []
        rating = entry[5] if len(entry) > 5 else None
        quote = entry[6] if len(entry) > 6 else None
        # The founder's row gives up its right end to the badge, so its
        # subtitle has less room than the others. Caught here rather than in a
        # render, which is how the same overlap got shipped on the agent groups.
        # The chevron-and-badge end of the row is spoken for, and a rating
        # takes more of it. Measuring the name to place the stars beside it was
        # the first attempt and it collided — a bold 13px name is wider than
        # any character estimate — so the stars sit at a fixed x and the
        # subtitle is held short enough to clear them.
        limit = 14 if rating is not None else (26 if badge else 34)
        if len(sub) > limit:
            raise ValueError(f"friend subtitle too long for the row: {sub!r}")
        h = 88 if quote else 74
        out.append(rrect(CX, yy, CW, h, 15, "url(#gCard)", C["line"], 1))
        if b64:
            out.append(face(CX + 33, yy + h / 2 - 8, 40, b64))
        else:
            out.append(orb(CX + 33, yy + h / 2 - 8, 19))

        out.append(text(CX + 62, yy + 26, name, 13, C["txt"], 700))
        out.append(text(CX + 62, yy + 41, sub, 9.5, C["t2"], 500))
        # The packs a profile carries, named rather than counted — "4 packs"
        # says how much it knows, the names say what about. Set small on
        # purpose: the names are the useful part, so more of them fitting beats
        # any of them being large. Overflows to +N rather than running under
        # the badge.
        if packs:
            avail = (CW - 52 - 12) - 62          # left edge to the badge
            shown, used = [], 0.0
            for i, nm in enumerate(packs):
                w = len(nm) * 3.2 + (5 if shown else 0)
                tail = 16 if i < len(packs) - 1 else 0
                if used + w + tail > avail:
                    break
                shown.append(nm)
                used += w
            line = " · ".join(shown)
            if len(shown) < len(packs):
                line += f"  +{len(packs) - len(shown)}"
            out.append(text(CX + 62, yy + 54, line, 6.5, C["cyan"], 600))
        # The rating and what somebody said about it, on one line at the
        # bottom. The stars answer "is this any good"; the line beside them
        # answers "good at what", and one without the other is half an answer.
        if rating is not None:
            out.append(stars(CX + 62, yy + 67, rating, C["gold"], 0.5))
            out.append(text(CX + 96, yy + 70, f"{rating:.1f}", 7.5,
                            C["gold"], 700))
            if quote:
                if len(quote) > 30:
                    raise ValueError(
                        f"review too long for the row: {quote!r}")
                out.append(text(CX + 114, yy + 70, quote, 7, C["t3"], 400))
        if badge:
            col = C["gold"] if badge == "VERIFIED" else C["brandA"]
            bw = 52
            bx = CX + CW - bw - 12
            out.append(rrect(bx, yy + h / 2 - 17, bw, 18, 9, A(col, 0.18),
                             col, 1))
            out.append(text(bx + bw / 2, yy + h / 2 - 5, badge, 7.5, col, 800,
                            "middle", 0.4))
        yy += h + 9
    return out, yy


def my_page(y, spec):
    """Somebody's own homepage — theme, tagline, Top 8.

    Drawn in the page's *own* colours rather than the app's, which is the
    entire point of the feature: a generated page looks like everybody else's,
    and the thing worth reviving from MySpace is that yours did not.
    """
    bg, ink, accent = spec["bg"], spec["ink"], spec["accent"]
    out = [rrect(CX, y, CW, 266, 16, bg, A(accent, 0.55), 1.4)]
    yy = y + 16
    out.append(face(CX + 40, yy + 24, 48, spec["face"]))
    out.append(text(CX + 74, yy + 18, spec["name"], 14, ink, 750))
    out.append(text(CX + 74, yy + 34, spec["handle"], 9.5, A(ink, 0.6), 500))
    out.append(rrect(CX + 74, yy + 42, 46, 15, 7, A(accent, 0.22), accent, 1))
    out.append(text(CX + 97, yy + 53, spec["badge"], 7, accent, 800,
                    "middle", 0.4))
    yy += 74            # clear of the badge above
    for line in spec["tagline"]:
        out.append(text(CX + 16, yy, line, 10.5, A(ink, 0.85), 500))
        yy += 14
    yy += 8
    out.append(text(CX + 16, yy, "TOP 8", 8, accent, 800, "start", 0.7))
    yy += 12
    for i, (nm, b64) in enumerate(spec["top"]):
        col, row = i % 4, i // 4
        fx = CX + 34 + col * 56
        fy = yy + 22 + row * 58
        out.append(face(fx, fy, 38, b64))
        out.append(text(fx, fy + 31, nm, 7, A(ink, 0.7), 600, "middle"))
    return out, y + 266 + 10


def agent_groups(y, groups):
    """Three tappable groups, one per light. The whole agent list, folded.

    A flat list of every running agent is the wrong shape for the screen
    somebody opens *because* a light went amber: it makes them scan for the
    one that changed. Grouping by light puts the answer first and the roster
    second, and it means the amber group is the one your thumb lands on.
    """
    out, yy = [], y
    for colour, label, n, sub in groups:
        # The chevron owns the right edge of the row. A sub that runs under it
        # reads as a rendering fault, so it is caught here rather than in a
        # screenshot somebody sends back weeks later.
        if len(sub) > 30:
            raise ValueError(f"agent group sub runs under the chevron: {sub!r}")
        col = {"green": C["green"], "amber": C["amber"], "red": C["red"]}[colour]
        h = 66
        out.append(rrect(CX, yy, CW, h, 16, "url(#gCard)", C["line"], 1))
        out.append(f'<circle cx="{CX+34}" cy="{yy+33}" r="17" fill="{A(col, 0.18)}"/>')
        out.append(f'<circle cx="{CX+34}" cy="{yy+33}" r="8" fill="{col}"/>')
        out.append(text(CX + 62, yy + 28, f"{n} {label}", 14.5, C["txt"], 700))
        out.append(text(CX + 62, yy + 46, sub, 10, C["t2"], 500))
        # The chevron is the whole affordance: these rows go somewhere.
        out.append(f'<path d="M{CX+CW-30} {yy+26} l8 7 -8 7" fill="none" '
                   f'stroke="{C["t3"]}" stroke-width="2" stroke-linecap="round"/>')
        yy += h + 10
    return out, yy


OVERLAY_ROWS = (("green", "running"), ("amber", "need help"), ("red", "stopped"))
# The floor the overlay sits on. Here that is the help button, not the tab
# bar: help is already parked in this corner on every screen, and two things
# competing for the same corner is worse than either of them being there.
OVERLAY_FLOOR = SY + SH - 84 - 17 - 12


def agent_overlay(counts):
    """The lights, floating over whatever screen you are actually on.

    This is the piece that makes the rest useful. An agent that only reports
    on its own screen is one you have to remember to go and check, and the
    states worth knowing about — amber and red — are exactly the ones nobody
    thinks to look for.

    Shaped like the watch face rather than as a full-width bar: a small
    translucent box in the bottom-right corner, three stacked rows, each its
    own tap target. A bar spanning the screen reads as chrome and cuts the
    content in half; a corner box reads as something floating above the work,
    which is what it is. Same three words as the wrist, so the two surfaces
    are never saying the same thing differently.
    """
    w, h = 112, 100
    x = SX + SW - w - 12
    y = OVERLAY_FLOOR - h
    out = [rrect(x, y, w, h, 14, "rgba(9,7,26,0.62)", A(C["brandA"], 0.5), 1)]
    yy = y + 22
    for (colour, word), n in zip(OVERLAY_ROWS, counts):
        col = {"green": C["green"], "amber": C["amber"], "red": C["red"]}[colour]
        dim = n == 0
        out.append(f'<circle cx="{x+16}" cy="{yy}" r="5" fill="{col}"'
                   + (' opacity="0.28"' if dim else "") + "/>")
        out.append(text(x + 28, yy + 4, str(n), 12.5,
                        col if not dim else C["t3"], 800))
        out.append(text(x + 40, yy + 4, word, 8.5,
                        C["t2"] if not dim else C["t3"], 600))
        yy += 24
    out.append(text(x + w / 2, y + h - 10, "open ›", 8, C["brandA"], 700, "middle"))
    return out


def meter(x, y, w, pct, grad):
    return (rrect(x, y, w, 7, 4, "#0d0a24", C["line"], 1)
            + rrect(x, y, max(6, w * pct), 7, 4, f"url(#{grad})"))


def spark(x, y, w, h, pts, col):
    n = len(pts)
    lo, hi = min(pts), max(pts)
    rng = (hi - lo) or 1
    coords = []
    for i, v in enumerate(pts):
        px = x + w * i / (n - 1)
        py = y + h - (v - lo) / rng * h
        coords.append(f"{px:.1f},{py:.1f}")
    endx, endy = coords[-1].split(",")
    return (f'<polyline points="{" ".join(coords)}" fill="none" stroke="{col}" '
            f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{endx}" cy="{endy}" r="3.2" fill="{col}"/>')


BUTTON_KINDS = ("brand", "danger", "amber", "ghost")


def button(x, y, w, label, kind="brand", h=42):
    # A misspelled kind used to fall through to `ghost` silently, so a button
    # meant to be the screen's primary action rendered as a faint outline and
    # nothing said so. Loud instead: the generator is the only thing that can
    # catch this, since the SVG is perfectly valid either way.
    if kind not in BUTTON_KINDS:
        raise ValueError(
            f"unknown button kind {kind!r} — one of {', '.join(BUTTON_KINDS)}")
    if kind == "brand":
        fill, tcol, st = "url(#gBrand)", "#fff", None
    elif kind == "danger":
        fill, tcol, st = A(C["red"], 0.16), C["red"], C["red"]
    elif kind == "amber":
        fill, tcol, st = "url(#gAmber)", "#20160a", None
    else:  # ghost
        fill, tcol, st = "rgba(255,255,255,0.06)", C["txt"], C["line"]
    return (rrect(x, y, w, h, 13, fill, st, 1)
            + text(x + w / 2, y + h / 2 + 4.5, label, 13, tcol, 700, "middle"))


def toggle(x, y, on):
    bg = C["green"] if on else "#2a2450"
    kx = x + 16 if on else x + 2
    return (rrect(x, y, 34, 20, 10, bg)
            + f'<circle cx="{kx+8}" cy="{y+10}" r="8" fill="#fff"/>')


def status_dot(x, y, label, tone):
    col = {"on": C["green"], "off": C["t3"], "avail": C["amber"], "crit": C["red"]}[tone]
    w = 14 + len(label) * 6.0
    return (rrect(x - w, y - 9, w, 16, 8, A(col, 0.14))
            + f'<circle cx="{x-w+9}" cy="{y-1}" r="3" fill="{col}"/>'
            + text(x - w + 16, y + 3, label, 9, col, 700, "start", 0.5))


# --------------------------------------------------------------------------- #
# frame
# --------------------------------------------------------------------------- #
PLATFORM = "ios"          # "ios" | "android"


def _status_icons(xr, y, col):
    o = []
    if PLATFORM == "android":
        o.append(rrect(xr - 9, y - 7, 8, 12, 1.5, "none", col, 1.2))
        o.append(rrect(xr - 7.5, y - 3, 5, 7, 1, col))
        o.append(f'<path d="M{xr-20} {y+5} L{xr-15} {y-4} L{xr-10} {y+5} Z" fill="{col}"/>')
        o.append(f'<path d="M{xr-33} {y+5} L{xr-33} {y-2} L{xr-25} {y+5} Z" fill="{col}"/>')
    else:
        o.append(rrect(xr - 22, y - 6, 20, 11, 3, "none", col, 1.1))
        o.append(rrect(xr - 20, y - 4, 14, 7, 2, col))
        o.append(rrect(xr - 1.4, y - 2.5, 2, 5, 1, col))
        o.append(f'<path d="M{xr-35} {y-1} a6 6 0 0 1 11 0" fill="none" stroke="{col}" stroke-width="1.3"/>')
        o.append(f'<circle cx="{xr-29.5}" cy="{y+3}" r="1.2" fill="{col}"/>')
        for i in range(4):
            o.append(rrect(xr - 52 + i * 4, y + 4 - (i + 1) * 1.9, 2.6, (i + 1) * 1.9, 0.8, col))
    return "".join(o)


def statusbar():
    tcol = C["silver"] if "silver" in C else C["t2"]
    notch = "#05070d"
    o = []
    if PLATFORM == "android":
        o.append(f'<circle cx="{W/2}" cy="{SY+12}" r="4.5" fill="{notch}"/>')
        o.append(f'<circle cx="{W/2}" cy="{SY+12}" r="4.5" fill="none" stroke="{C["line"]}" stroke-width="1"/>')
    else:
        o.append(rrect(W / 2 - 30, SY + 5, 60, 15, 7.5, notch))
    o.append(text(SX + 14, SY + 34, "9:41", 11, tcol, 600))
    o.append(_status_icons(SX + SW - 14, SY + 34, tcol))
    return o


def help_button():
    """The help affordance, on every screen.

    Drawn here rather than per screen because "on all screens" is a property
    of the chrome, not something 79 screens can each be trusted to remember —
    and the one screen that forgets is the one somebody is stuck on.

    Above the tab bar and on the trailing edge, where it is reachable by a
    thumb and out of the way of the primary action. Deliberately unbranded and
    faceless: on a product whose subject is synthetic people who look real, a
    help assistant with a portrait would be a thirty-fifth character.
    """
    r = 17
    cx = SX + SW - 30
    cy = SY + SH - 84
    return [
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{A(C["brandA"], 0.16)}"'
        f' stroke="{C["brandA"]}" stroke-width="1.2"/>',
        text(cx, cy + 5, "?", 17, C["brandA"], 800, "middle"),
    ]


def navbar():
    o = []
    yb = SY + SH - 6
    if PLATFORM == "android":
        cx = W / 2
        o.append(f'<path d="M{cx-34+5} {yb-4.5} L{cx-34-5} {yb} L{cx-34+5} {yb+4.5} Z" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.3" stroke-linejoin="round"/>')
        o.append(f'<circle cx="{cx}" cy="{yb}" r="4.6" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.3"/>')
        o.append(rrect(cx + 34 - 4.6, yb - 4.6, 9.2, 9.2, 1.6, "none", "rgba(255,255,255,0.5)", 1.3))
    else:
        o.append(rrect(W / 2 - 42, yb - 1, 84, 4, 2, "rgba(255,255,255,0.6)"))
    return o


def defs(ac):
    """The gradients every screen shares. Split out of :func:`head` so a
    full-bleed screen — which has no title bar to hang them off — can still
    open with the same palette instead of growing a second copy."""
    return f'''<defs>
      <linearGradient id="gScr" x1="0" y1="0" x2="0.6" y2="1">
        <stop offset="0" stop-color="{C['scrA']}"/><stop offset="1" stop-color="{C['scrB']}"/></linearGradient>
      <linearGradient id="gFrame" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="{C['frameA']}"/><stop offset="1" stop-color="{C['frameB']}"/></linearGradient>
      <linearGradient id="gCard" x1="0" y1="0" x2="0.4" y2="1">
        <stop offset="0" stop-color="{C['card']}"/><stop offset="1" stop-color="{C['card2']}"/></linearGradient>
      <linearGradient id="gBrand" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="gAmber" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="{C['amber']}"/><stop offset="1" stop-color="#ffd27a"/></linearGradient>
      <linearGradient id="mV" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="mA" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['amber']}"/><stop offset="1" stop-color="#ff9f45"/></linearGradient>
      <linearGradient id="mG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5fb87a"/><stop offset="1" stop-color="{C['green']}"/></linearGradient>
      <linearGradient id="mC" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6bb6d6"/><stop offset="1" stop-color="{C['cyan']}"/></linearGradient>
      <radialGradient id="orb" cx="36%" cy="30%" r="78%">
        <stop offset="0" stop-color="#d9ccff"/><stop offset="38%" stop-color="{C['brandA']}"/>
        <stop offset="78%" stop-color="#3f3bc0"/><stop offset="100%" stop-color="#140f34"/></radialGradient>
      <radialGradient id="glow" cx="50%" cy="50%" r="50%">
        <stop offset="0" stop-color="{ac}" stop-opacity="0.5"/><stop offset="1" stop-color="{ac}" stop-opacity="0"/></radialGradient>
    </defs>'''


def head(num, title, sub, accent="brand", locked=False):
    ac = ACCENT.get(accent, C["brandA"])
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)} screen">',
           defs(ac)]
    out.append(rrect(PX, PY, PW, PH, 40, "url(#gFrame)"))
    out.append(rrect(SX, SY, SW, SH, 31, "url(#gScr)"))
    out += statusbar()
    lockmark = "  🔒" if locked else ""
    out.append(text(CX, SY + 66, title, 20, C["txt"], 700, spacing=-0.4))
    if locked:
        lx = CX + len(title) * 11.2 + 18
        out.append(icon("lock", lx, SY + 60, C["amber"], 0.66))
    if sub:
        out.append(text(CX, SY + 84, sub, 11.5, C["t2"], 400))
    return out


def tabbar(tabs, active):
    out = [rrect(SX, SY + SH - 52, SW, 52, 0, C["tab"])]
    out.append(f'<rect x="{SX}" y="{SY+SH-52}" width="{SW}" height="1" fill="{C["line"]}"/>')
    step = SW / len(tabs)
    for i, (ic, lbl) in enumerate(tabs):
        cx = SX + step * i + step / 2
        on = (i == active)
        col = C["brandA"] if on else C["t3"]
        out.append(icon(ic, cx, SY + SH - 34, col, 0.72))
        out.append(text(cx, SY + SH - 12, lbl, 8.2, col, 600, "middle"))
    return out


MAIN = [("target", "Home"), ("people", "Relationships"), ("chart", "Stats"), ("gear", "More")]
VAULT = [("lock", "Vault"), ("search", "Search"), ("clock", "Timeline"), ("gear", "Settings")]
MARKET = [("compass", "Discover"), ("grid", "Categories"), ("heart", "My List"), ("list", "Listings")]
LICENSE = [("doc", "Licenses"), ("gift", "Grants"), ("coin", "Earnings"), ("gear", "Settings")]
CONTROL = [("lock", "Privacy"), ("shield", "Security"), ("gear", "Settings"), ("info", "About")]
REL = [("people", "Relationships"), ("net", "Network"), ("shield", "Boundaries"), ("gear", "More")]


def close():
    return ['</svg>']


# --------------------------------------------------------------------------- #
# building blocks
# --------------------------------------------------------------------------- #
def card_room(c):
    """How much room a card's title and subtitle actually have, in px.

    The title shares its line with a pill; the subtitle passes underneath one,
    so only the title pays for it. A metric is set large against the right edge
    at the card's vertical centre, which is level with both.

    The margins here are the *breakage* line, not the design's. Cards are laid
    out to 14px of inner padding; this checks against 8, because the measuring
    font is Cairo's DejaVu and the browsers that actually render these SVGs
    find SF Pro, Segoe UI or Roboto — all narrower. Checking the design's own
    padding against the widest possible font would fail text that looks fine
    everywhere it is ever seen.
    """
    tx = CX + 56 if c.get("icon") else CX + 14
    right = CX + CW - 8
    if c.get("metric"):
        right -= tw.width(c["metric"], 20, 750) + 4
    # A status dot is set at the card's vertical centre, so unlike a pill it is
    # level with the subtitle too. Missing that let `REQUIRED` sit on top of
    # "verified before any chat" on the adult-mode screen.
    if c.get("stat"):
        right -= 14 + 6.0 * len(c["stat"][0]) + 4
    title_right = right
    if c.get("pill"):
        title_right -= (12 + tw.width(c["pill"][0], 9.5, 700)
                        + 0.4 * len(c["pill"][0]) + 4)
    return title_right - tx, right - tx


def card_block(y, c):
    # Nothing on these screens wraps or ellipsises, so text that does not fit
    # runs off the side of the phone and stays there. Three cards on the gaming
    # screen did exactly that and survived a full gallery rebuild, because the
    # only thing that would have caught it was somebody looking at that one
    # screen. Measured rather than counted — `Companion` and `lllllllll` are
    # both nine characters and one is nearly twice as wide.
    title_room, sub_room = card_room(c)
    have = tw.width(c["k"], 13, 600)
    if have > title_room:
        raise ValueError(f"card title runs off the card: {c['k']!r} needs "
                         f"{have:.0f}px, has {title_room:.0f}px")
    if c.get("s"):
        have = tw.width(c["s"], 11, 400)
        if have > sub_room:
            raise ValueError(f"card subtitle runs off the card: {c['s']!r} "
                             f"needs {have:.0f}px, has {sub_room:.0f}px")
    h = c.get("h", 52)
    extra = c.get("extra")
    if extra and extra[0] in ("meter", "spark"):
        h = 66
    out = [rrect(CX, y, CW, h, 16, "url(#gCard)", C["line"], 1)]
    tx = CX + 14
    if c.get("icon"):
        out.append(chip(CX + 12, y + (h - 34) / 2 if not extra else y + 9, c["icon"], ACCENT[c["color"]]))
        tx = CX + 56
    ty = y + (26 if extra else h / 2 - 6)
    out.append(text(tx, ty, c["k"], 13, C["txt"], 600))
    if c.get("s"):
        out.append(text(tx, ty + 15, c["s"], 11, C["t2"]))
    if c.get("metric"):
        out.append(text(CX + CW - 14, y + h / 2 + 7, c["metric"], 20, C["txt"], 750, "end"))
    if c.get("pill"):
        out.append(pill(CX + CW - 14, y + 20, c["pill"][0], c["pill"][1]))
    if c.get("stat"):
        out.append(status_dot(CX + CW - 14, y + h / 2, c["stat"][0], c["stat"][1]))
    if extra:
        if extra[0] == "meter":
            out.append(meter(tx, y + h - 16, CW - (tx - CX) - 14, extra[1], extra[2]))
        elif extra[0] == "spark":
            out.append(spark(tx, y + h - 30, CW - (tx - CX) - 16, 22, extra[1], ACCENT[extra[2]]))
    return "".join(out), y + h + 10


def check_row(y, ic, col, k, s, count, on=True):
    out = [rrect(CX, y, CW, 46, 14, "url(#gCard)", C["line"], 1)]
    out.append(chip(CX + 10, y + 6, ic, ACCENT[col]))
    out.append(text(CX + 54, y + 20, k, 12.5, C["txt"], 600))
    out.append(text(CX + 54, y + 34, s, 10.5, C["t2"]))
    if count:
        out.append(text(CX + CW - 40, y + 27, count, 11, C["t2"], 500, "end"))
    if on:
        out.append(f'<circle cx="{CX+CW-20}" cy="{y+23}" r="9" fill="{A(C["green"],0.18)}" stroke="{C["green"]}" stroke-width="1"/>')
        out.append(icon("shieldok", CX + CW - 20, y + 23, C["green"], 0.42) if False else
                   f'<path d="M{CX+CW-24} {y+23} l{2.6} {3} {5} -{5.5}" fill="none" stroke="{C["green"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    else:
        out.append(f'<circle cx="{CX+CW-20}" cy="{y+23}" r="9" fill="none" stroke="{C["t3"]}" stroke-width="1.4"/>')
    return "".join(out), y + 54


def person_row(y, initial, col, name, rel, tone_label, tone):
    out = [rrect(CX, y, CW, 50, 14, "url(#gCard)", C["line"], 1)]
    out.append(f'<circle cx="{CX+26}" cy="{y+25}" r="15" fill="{A(col,0.20)}" stroke="{col}" stroke-width="1.2"/>')
    out.append(text(CX + 26, y + 30, initial, 14, col, 800, "middle"))
    out.append(text(CX + 52, y + 22, name, 12.5, C["txt"], 650))
    out.append(text(CX + 52, y + 37, rel, 10.5, C["t2"]))
    out.append(pill(CX + CW - 14, y + 25, tone_label, tone))
    return "".join(out), y + 58


# The character these screens depict. A screen with a real face on it should
# carry that person's name and profession — "AI assistant" belongs in the
# chrome that *cannot* know who is loaded, not on a page showing somebody.
# Both come from seed.py by way of frames.PORTRAITS, so the face and the name
# cannot drift apart.
CHARACTER = "Marcus Bell"
CHARACTER_ROLE = "retired fee-only financial planner"


def _face_of(name):
    for who, b64 in frames.PORTRAITS:
        if who == name:
            return b64
    raise SystemExit(f"no portrait for {name!r} in frames.PORTRAITS")


def _assistant_face():
    """The character's portrait, used wherever their face appears, so the
    screens read as one person rather than a different one per screen."""
    return _face_of(CHARACTER)


def face(cx, cy, size, b64, radius=None):
    """A real portrait, centred in a rounded box.

    These places used to draw :func:`orb` — a purple sphere with a generic
    person glyph — where the *face* belongs. The pixels were already in the
    repo: all 34 starter portraits ride in `frames.PORTRAITS`, and exactly one
    screen used them. So the screens showed a hologram of a profile whose
    photograph was sitting one import away.

    **A rounded box rather than a circle, and that is not only taste.**
    `tools/mark_portraits.py` burns the AI mark into the pixels at the
    *top-right*, so a circular clip of a square portrait cuts the corner the
    disclosure lives in. The radius here stays well inside it, so the mark
    survives into every screen that shows a face — which is the whole reason
    it was burned in rather than composited.
    """
    r = size / 2
    rad = radius if radius is not None else size * 0.28
    x, y = cx - r, cy - r
    cid = f"fc{abs(hash((cx, cy, size))) % 100000}"
    return "".join([
        f'<circle cx="{cx}" cy="{cy}" r="{r*1.45:.1f}" fill="url(#glow)"/>',
        f'<defs><clipPath id="{cid}">'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}"'
        f' rx="{rad:.1f}"/></clipPath></defs>',
        f'<image href="data:image/jpeg;base64,{b64}" x="{x:.1f}" y="{y:.1f}"'
        f' width="{size}" height="{size}" preserveAspectRatio="xMidYMid slice"'
        f' clip-path="url(#{cid})"/>',
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}"'
        f' rx="{rad:.1f}" fill="none" stroke="rgba(255,255,255,0.22)"'
        f' stroke-width="1"/>',
    ])


def orb(cx, cy, r, head_profile=False):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r*1.5:.1f}" fill="url(#glow)"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#orb)"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="rgba(255,255,255,0.20)" stroke-width="1"/>',
           f'<ellipse cx="{cx-r*0.28:.1f}" cy="{cy-r*0.34:.1f}" rx="{r*0.30:.1f}" ry="{r*0.18:.1f}" fill="rgba(255,255,255,0.40)"/>']
    if head_profile:
        # simple facing-left head/brain profile line, echoing the launch mockup
        out.append(f'<path d="M{cx+r*0.5:.1f} {cy+r*0.55:.1f} '
                   f'C{cx-r*0.1:.1f} {cy+r*0.62:.1f},{cx-r*0.62:.1f} {cy+r*0.34:.1f},{cx-r*0.6:.1f} {cy-r*0.06:.1f} '
                   f'C{cx-r*0.58:.1f} {cy-r*0.5:.1f},{cx-r*0.2:.1f} {cy-r*0.66:.1f},{cx+r*0.16:.1f} {cy-r*0.6:.1f} '
                   f'C{cx+r*0.5:.1f} {cy-r*0.54:.1f},{cx+r*0.6:.1f} {cy-r*0.2:.1f},{cx+r*0.4:.1f} {cy+r*0.05:.1f}" '
                   f'fill="none" stroke="rgba(255,255,255,0.85)" stroke-width="1.6" stroke-linecap="round"/>')
        for dx, dy in [(-0.18, -0.18), (0.02, -0.28), (0.16, -0.06), (-0.1, 0.12), (0.22, 0.14)]:
            out.append(f'<circle cx="{cx+r*dx:.1f}" cy="{cy+r*dy:.1f}" r="1.5" fill="rgba(255,255,255,0.9)"/>')
    return "".join(out)


def ring(cx, cy, r, pct, col, sw=9):
    circ = 2 * math.pi * r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{A(col,0.16)}" stroke-width="{sw}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-dasharray="{circ*pct:.1f} {circ:.1f}" '
            f'transform="rotate(-90 {cx} {cy})"/>')


def statbar(y, label, pct, val, col):
    out = [text(CX, y, label, 12, C["txt"], 600),
           text(CX + CW, y, val, 12, col, 750, "end"),
           rrect(CX, y + 8, CW, 7, 4, "#0d0a24", C["line"], 1),
           rrect(CX, y + 8, max(8, CW * pct), 7, 4, col)]
    return "".join(out), y + 30


def qr(qx, qy, qs, seed=7):
    import random
    random.seed(seed)
    out = [rrect(qx, qy, qs, qs, 14, "#ffffff")]
    cell = (qs - 20) / 21

    def finder(r, c):
        res = []
        for i in range(7):
            for j in range(7):
                on = i in (0, 6) or j in (0, 6) or (2 <= i <= 4 and 2 <= j <= 4)
                if on:
                    res.append(rrect(qx + 10 + (c + j) * cell, qy + 10 + (r + i) * cell, cell, cell, 0, "#140f34"))
        return "".join(res)
    grid = []
    for r in range(21):
        for c in range(21):
            if (r < 8 and c < 8) or (r < 8 and c > 12) or (r > 12 and c < 8):
                continue
            if random.random() > 0.5:
                grid.append(rrect(qx + 10 + c * cell, qy + 10 + r * cell, cell, cell, 0, "#140f34"))
    out.append("".join(grid) + finder(0, 0) + finder(0, 14) + finder(14, 0))
    return "".join(out)


def apple_mark(x, y, s=0.66, col="#0b0b0f"):
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s})" fill="{col}">'
            '<path d="M16.365 1.43c0 1.14-.493 2.27-1.177 3.08-.744.9-1.99 1.57-2.987 1.49'
            '-.12-1.15.42-2.35 1.07-3.08.72-.81 2.02-1.47 3.09-1.49z'
            'M20.5 17.06c-.06.14-.94 3.22-3.1 3.25-1.75.02-2.31-1.04-4.31-1.04-2 0-2.62 1.02-4.28 1.06'
            '-2.09.08-3.68-3.29-3.74-3.43-.06-.14-1.62-6.18 1.32-9.03.98-.96 2.36-1.5 3.65-1.5'
            ' 1.75 0 2.82 1.05 4.25 1.05 1.37 0 2.2-1.05 4.28-1.05 1.03 0 2.6.42 3.6 1.66'
            '-3.16 1.73-2.65 6.24.53 8.03z"/></g>')


def google_mark(x, y, s=0.66):
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s})">'
            '<path fill="#4285F4" d="M23.06 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h6.2a5.3 5.3 0 0 1-2.3 3.48v2.89h3.72c2.18-2 3.44-4.96 3.44-8.38z"/>'
            '<path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.94-2.91l-3.72-2.89c-1.03.69-2.35 1.1-4.22 1.1-3.25 0-6-2.19-6.98-5.13H1.18v2.98A12 12 0 0 0 12 24z"/>'
            '<path fill="#FBBC05" d="M5.02 14.27a7.2 7.2 0 0 1 0-4.54V6.75H1.18a12 12 0 0 0 0 10.5l3.84-2.98z"/>'
            '<path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.3-3.3C17.95 1.19 15.24 0 12 0A12 12 0 0 0 1.18 6.75l3.84 2.98C6 6.94 8.75 4.75 12 4.75z"/></g>')


def envelope(cx, cy, col):
    return (f'<rect x="{cx-9:.1f}" y="{cy-6:.1f}" width="18" height="13" rx="2.5" fill="none" stroke="{col}" stroke-width="1.7"/>'
            f'<path d="M{cx-8:.1f} {cy-4:.1f} L{cx:.1f} {cy+2:.1f} L{cx+8:.1f} {cy-4:.1f}" fill="none" stroke="{col}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>')


# --------------------------------------------------------------------------- #
# screen renderer
# --------------------------------------------------------------------------- #
def photo(x, y, w, h, data, tag=None, note=None, uid="ph"):
    """A real camera frame, embedded rather than linked.

    An SVG rendered through an ``<img>`` tag — which is how GitHub shows one in
    a README — cannot fetch external files, so a relative path to the `.webp`
    would render as an empty box. The pixels ride inside the file as a data
    URI; see tools/encode_desk_frames.py.

    Deliberately **no AI watermark**: these are photographs of real rooms
    belonging to real people. Marking one would be a false statement about
    both the room and the person who is about to walk back into it.
    """
    cid = f"clip{uid}"
    o = [f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" '
         f'height="{h}" rx="14"/></clipPath>',
         f'<image x="{x}" y="{y}" width="{w}" height="{h}" '
         f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})" '
         f'href="data:image/jpeg;base64,{data}"/>',
         # A hairline over the photo so it sits in the design language rather
         # than looking pasted on top of it.
         rrect(x, y, w, h, 14, "none", A(C["line"], 0.9), 1)]
    if tag:
        label, tone = tag
        col = {"live": C["red"], "sample": C["t2"]}[tone]
        tw = 16 + len(label) * 6.2
        o.append(rrect(x + 10, y + 10, tw, 20, 10, "rgba(8,6,20,0.72)"))
        o.append(f'<circle cx="{x+21}" cy="{y+20}" r="3.4" fill="{col}"/>')
        o.append(text(x + 29, y + 24, label, 9, "#fff", 750, "start", 0.4))
    if note:
        o.append(rrect(x, y + h - 30, w, 30, 0, "rgba(8,6,20,0.66)"))
        o.append(text(x + 12, y + h - 11, note, 9.2, "#e8e4ff", 600))
    return "".join(o)


def live_overlay(x, y, w, h, comments, ticker, viewers=None):
    """Chat, likes, shares and gifts drawn *over* the picture.

    This is where a viewer is already looking. Putting the reactions in a
    panel beside the video means moving their eyes off the thing they came
    for, and on a stream whose whole premise is an empty chair with a bell,
    the reactions *are* the room. So they float on the frame at ~80% opacity:
    legible, and the picture still readable underneath.
    """
    o = []
    if viewers:
        vw = 14 + len(viewers) * 5.6
        o.append(rrect(x + w - vw - 10, y + 10, vw, 20, 10, "rgba(8,6,20,0.62)"))
        o.append(text(x + w - vw / 2 - 10, y + 24, viewers, 9, "#e8e4ff", 650,
                      "middle"))
    # The reaction ticker climbs the right edge, the way it does on a stream.
    ty = y + h - 46
    for ic, col, label in ticker:
        cw_ = 30 + len(label) * 5.4
        o.append(rrect(x + w - cw_ - 10, ty, cw_, 22, 11, "rgba(8,6,20,0.58)"))
        o.append(icon(ic, x + w - cw_ + 2, ty + 11, ACCENT[col], 0.52))
        o.append(text(x + w - 18, ty + 15, label, 8.6, "#efecff", 650, "end"))
        ty -= 26
    # Chat runs down the top-left, under the LIVE badge, oldest first.
    #
    # A stream would normally stack it up from the bottom, and that is what I
    # built first — but the sign is the subject of both of these frames
    # ("ring bell for service, away from the desk"; "be back soon or ring
    # bell"), and they sit at different heights in the two photos, so no
    # bottom anchor clears both. Chat over the sign is chat over the entire
    # reason the stream is worth watching. The top strip is empty in both.
    cy = y + 38
    n = len(comments)
    for i, (who, said) in enumerate(comments):
        line = f"{who}  {said}"
        # +26 for the avatar that sits inside the left end of the plate.
        lw = min(40 + len(line) * 4.6, w - 104)
        # The *plate* is transparent so the room stays visible through it;
        # the text on top is not. Chat you have to squint at is chat nobody
        # reads, and these lines are the room talking.
        plate = 0.46 + 0.14 * (i + 1) / n
        o.append(rrect(x + 10, cy, lw, 22, 11, f"rgba(8,6,20,{plate:.2f})"))
        # Who said it, as a small avatar on the line — a silhouette, not a
        # portrait and not an initial. These are viewers rather than
        # synthetic profiles, so there is no likeness to draw, and drawing
        # one would be inventing a face for someone who never gave us theirs.
        # The tint is derived from the name, so the same person keeps the
        # same colour down the thread.
        acx, acy, ar = x + 22, cy + 11, 8.0
        tint = ACCENT[("brand", "cyan", "pink", "amber", "green")[
            sum(map(ord, who)) % 5]]
        o.append(f'<circle cx="{acx}" cy="{acy}" r="{ar}" '
                 f'fill="{A(tint, 0.30)}" stroke="{A(tint, 0.85)}" '
                 f'stroke-width="1"/>')
        o.append(icon("person", acx, acy, "rgba(255,255,255,0.92)", 0.42))
        o.append(text(acx + ar + 6, cy + 15, line, 8.4,
                      f"rgba(245,242,255,{0.88 + 0.12 * (i + 1) / n:.2f})", 650))
        # 24, not 26. The avatars made each line taller, and left alone that
        # pushed the last line down onto the sign on the stage frame. The
        # block still starts where it did — it just ends 4px higher.
        cy += 24
    return "".join(o)


def portrait_grid(x, y, w, cols, entries, cell_gap=6, uid="pg"):
    """The starter collection, as the faces themselves.

    The screen used to say "seeded with faces" and then show icon chips,
    which is the one thing a screen about portraits must not do. Every face
    here already carries the AI mark burned into its own pixels, so the grid
    needs no badge of its own — the disclosure is in the image, which is the
    whole point of having burned it in rather than drawn it at render time.
    """
    o = []
    cell = (w - cell_gap * (cols - 1)) / cols
    for i, (_name, data) in enumerate(entries):
        cx = x + (i % cols) * (cell + cell_gap)
        cy = y + (i // cols) * (cell + cell_gap)
        cid = f"pc{uid}{i}"
        o.append(f'<clipPath id="{cid}"><rect x="{cx:.1f}" y="{cy:.1f}" '
                 f'width="{cell:.1f}" height="{cell:.1f}" rx="9"/></clipPath>')
        o.append(f'<image x="{cx:.1f}" y="{cy:.1f}" width="{cell:.1f}" '
                 f'height="{cell:.1f}" preserveAspectRatio="xMidYMid slice" '
                 f'clip-path="url(#{cid})" '
                 f'href="data:image/jpeg;base64,{data}"/>')
        o.append(rrect(cx, cy, cell, cell, 9, "none", A(C["line"], 0.85), 1))
    rows = -(-len(entries) // cols)
    return "".join(o), rows * (cell + cell_gap) - cell_gap


def render(spec):
    num = spec["num"]
    out = head(f"{num:02d}", spec["title"], spec.get("sub", ""),
               spec.get("accent", "brand"), spec.get("locked", False))
    y = SY + 100
    hero = spec.get("hero")

    # An agent's status light, when the screen is showing one at work. Sits
    # directly under the subtitle, above everything else, because "does this
    # need me" is the first question and should not be somewhere you scroll to.
    if spec.get("light"):
        colour, label = spec["light"]
        out.append(agent_light(CX + 8, y - 6, colour, label))
        y += 22

    if spec.get("groups"):
        block, y = agent_groups(y, spec["groups"])
        out += block
        y += 4

    if spec.get("friends"):
        block, y = friends_list(y, spec["friends"])
        out += block
        y += 4

    if spec.get("my_page"):
        block, y = my_page(y, spec["my_page"])
        out += block

    # A camera frame above the cards. Runs before the hero chain because a
    # screen has either a hero or cards, never both — this is the one thing
    # that sits above whichever it is.
    if spec.get("grid"):
        block, gh = portrait_grid(CX, y, CW, spec.get("grid_cols", 5),
                                  spec["grid"], uid=f"{num:02d}")
        out.append(block)
        y += gh + 14

    if spec.get("facade_card"):
        f = spec["facade_card"]
        out.append(video_facade(CX, y, CW, 152, f["platform"], f["title"],
                                f["note"], uid=f"{num:02d}"))
        y += 164

    if spec.get("photo"):
        ph = spec.get("photo_h", 148)
        out.append(photo(CX, y, CW, ph, spec["photo"],
                         tag=spec.get("photo_tag"),
                         note=None if spec.get("overlay") else spec.get("photo_note"),
                         uid=f"{num:02d}"))
        if spec.get("overlay"):
            ov = spec["overlay"]
            out.append(live_overlay(CX, y, CW, ph, ov.get("comments", []),
                                    ov.get("ticker", []), ov.get("viewers")))
        # Over the picture, anchored to its bottom — an overlay drawn before
        # the photo is a list above a picture, which is the thing it exists
        # not to be.
        bottom = 12
        if spec.get("live_bar"):
            block, used = live_bar(CX, y, CW, ph, spec["live_bar"])
            out += block
            # The chat gives way to the bar rather than the other way round: a
            # comment you cannot read scrolls past, a control you cannot reach
            # never gets used.
            bottom += used
        if spec.get("bubble_chat"):
            rows = spec["bubble_chat"]
            block, _ = bubble_chat(CX + 8, y + ph - bottom - len(rows) * 30,
                                   CW - 16, rows)
            out += block
        y += ph + 12

    if hero == "welcome":
        out.append(orb(W / 2, y + 52, 42, head_profile=True))
        y += 112
        out.append(text(W / 2, y + 6, "Your identity.", 19, "#fff", 750, "middle", -0.3))
        out.append(text(W / 2, y + 28, "Your AI. Your control.", 19, "#fff", 750, "middle", -0.3))
        out.append(text(W / 2, y + 50, "A synthetic profile that thinks,", 11.5, C["t2"], 400, "middle"))
        out.append(text(W / 2, y + 66, "remembers, and evolves with you.", 11.5, C["t2"], 400, "middle"))
        y += 92
        out.append(button(CX, y, CW, "Create My Profile", "brand", 44))
        out.append(button(CX, y + 54, CW, "Import Existing Profile", "ghost", 44))
        out.append(icon("lock", W / 2 - 98, y + 129, C["amber"], 0.52))
        out.append(text(W / 2 + 6, y + 133, "AES-256 Protected · Your data. Your vault.", 9.3, C["t3"], 500, "middle"))

    elif hero == "types":
        rows = [("person", "brand", "Myself", "Digital extension of me"),
                ("people", "amber", "Family Legacy", "Preserve memories"),
                ("mask", "pink", "Fictional Persona", "Create someone new"),
                ("star2", "gold", "Creator Persona", "Your AI brand"),
                ("building", "cyan", "Enterprise Agent", "Business knowledge")]
        for ic, col, k, s in rows:
            out.append(rrect(CX, y, CW, 50, 14, "url(#gCard)", C["line"], 1))
            out.append(chip(CX + 10, y + 8, ic, ACCENT[col]))
            out.append(text(CX + 54, y + 22, k, 13, C["txt"], 650))
            out.append(text(CX + 54, y + 37, s, 10.5, C["t2"]))
            out.append(text(CX + CW - 16, y + 30, "›", 18, C["t3"], 400, "end"))
            y += 58
        out.append(rrect(CX, y + 2, CW, 44, 14, A(C["brandA"], 0.10), C["brandA"], 1))
        out.append(icon("bolt", CX + 24, y + 24, C["brandA"], 0.8))
        out.append(text(CX + 44, y + 20, "Can't decide? Start with Genesis", 11, C["txt"], 600))
        out.append(text(CX + 44, y + 34, "4 questions to birth your AI", 10, C["t2"]))

    elif hero == "sources":
        rows = [("photo", "brand", "Photos", "245 items"),
                ("mic", "pink", "Voice Notes", "38 items"),
                ("chat", "cyan", "Messages", "1,024 items"),
                ("pen", "amber", "Writing", "312 items"),
                ("cal", "green", "Life Events", "89 items"),
                ("db", "gold", "Knowledge", "156 items")]
        for ic, col, k, cnt in rows:
            s, y = check_row(y, ic, col, k, cnt, "", on=True)
            out.append(s)
        out.append(button(CX, y + 2, CW, "+  Add Source", "brand", 40))
        y += 52
        out.append(icon("lock", CX + 6, y + 6, C["cyan"], 0.6))
        out.append(text(CX + 18, y + 10, "Stored in your vault · optional cloud contribution", 9.3, C["t3"], 500))

    elif hero == "personality":
        y += 8
        sliders = [("Warmth", 0.7), ("Humor", 0.55), ("Formality", 0.4), ("Creativity", 0.78)]
        for lbl, v in sliders:
            out.append(text(CX, y, lbl, 12.5, C["txt"], 600))
            out.append(rrect(CX, y + 10, CW, 6, 3, "#0d0a24", C["line"], 1))
            out.append(rrect(CX, y + 10, CW * v, 6, 3, "url(#gBrand)"))
            out.append(f'<circle cx="{CX+CW*v:.1f}" cy="{y+13}" r="9" fill="#fff"/>')
            out.append(f'<circle cx="{CX+CW*v:.1f}" cy="{y+13}" r="9" fill="none" stroke="{C["brandA"]}" stroke-width="2"/>')
            y += 40
        out.append(text(CX, y + 4, "Boundaries & Maturity", 12.5, C["txt"], 700))
        y += 14
        seg = ["Strict", "Balanced", "Open"]
        out.append(rrect(CX, y, CW, 38, 12, "#0d0a24", C["line"], 1))
        sw = (CW - 8) / 3
        for i, lbl in enumerate(seg):
            on = (i == 1)
            if on:
                out.append(rrect(CX + 4 + i * sw, y + 4, sw, 30, 9, "url(#gBrand)"))
            out.append(text(CX + 4 + i * sw + sw / 2, y + 24, lbl, 12, "#fff" if on else C["t2"], 650, "middle"))
        y += 46
        out.append(text(W / 2, y, "Minors always use Strict filters", 9.5, C["t3"], 500, "middle"))
        y += 16
        out.append(button(CX, y, CW, "Continue", "brand", 44))

    elif hero == "profilehome":
        cx0 = W / 2
        out.append(face(cx0, y + 42, 84, _assistant_face()))
        out.append(text(cx0, y + 98, CHARACTER, 21, "#fff", 750, "middle"))
        out.append(text(cx0, y + 116, CHARACTER_ROLE, 10.5, C["t2"], 500, "middle"))
        out.append(f'<circle cx="{cx0-30}" cy="{y+130}" r="3" fill="{C["green"]}"/>')
        out.append(text(cx0 - 22, y + 134, "Online", 10.5, C["green"], 600))
        y += 150
        gw = (CW - 10) / 2
        cells = [("Memory", "247", "entries", C["brandA"]),
                 ("Relationships", "12", "connections", C["amber"]),
                 ("Engagement", "92%", "High", C["green"]),
                 ("Security", "Vault", "Protected", C["cyan"])]
        for i, (k, v, s, col) in enumerate(cells):
            gx = CX + (i % 2) * (gw + 10)
            gy = y + (i // 2) * 62
            out.append(rrect(gx, gy, gw, 54, 14, "url(#gCard)", C["line"], 1))
            out.append(text(gx + 12, gy + 20, k, 10, C["t2"], 500))
            if v == "Vault":
                out.append(icon("lock", gx + 20, gy + 38, col, 0.7))
                out.append(text(gx + 34, gy + 42, s, 11, col, 650))
            else:
                out.append(text(gx + 12, gy + 42, v, 19, col, 800))
                out.append(text(gx + gw - 12, gy + 42, s, 9.5, C["t2"], 500, "end"))
        y += 132
        out.append(button(CX, y, CW, "Chat", "brand", 42))
        out.append(button(CX, y + 50, (CW - 10) / 2, "Customize", "ghost", 38))
        out.append(button(CX + (CW - 10) / 2 + 10, y + 50, (CW - 10) / 2, "View Memory", "ghost", 38))

    elif hero == "chat":
        out.append(f'<circle cx="{CX+13}" cy="{y+11}" r="13" fill="url(#orb)"/>')
        # The dot and "Online" used to sit at a fixed x that assumed a
        # three-letter name. Measured off the label instead, so the status
        # cannot be overwritten by a longer one.
        _label = "AI assistant"
        out.append(text(CX + 32, y + 8, _label, 12, C["txt"], 650))
        _dot = CX + 32 + len(_label) * 6.4 + 10
        out.append(f'<circle cx="{_dot}" cy="{y+5}" r="2.5" fill="{C["green"]}"/>')
        out.append(text(_dot + 6, y + 8, "Online", 9.5, C["green"], 600))
        y += 24
        # AI bubble
        out.append(rrect(CX, y, CW - 40, 66, 14, "url(#gCard)", C["line"], 1))
        for i, ln in enumerate(["Hey David, I noticed you haven't", "checked in this week.",
                                 "Want to talk about the garden? 🌱"]):
            out.append(text(CX + 14, y + 22 + i * 15, ln, 11, C["txt"], 400))
        y += 78
        # user bubble
        out.append(rrect(CX + 60, y, CW - 60, 40, 14, "url(#gBrand)"))
        out.append(text(CX + CW - 14, y + 17, "Hey! I've been busy,", 10.5, "#fff", 500, "end"))
        out.append(text(CX + CW - 14, y + 32, "but thinking about you.", 10.5, "#fff", 500, "end"))
        y += 52
        # context panel
        out.append(rrect(CX, y, CW, 78, 14, A(C["brandA"], 0.08), C["brandA"], 1))
        out.append(icon("lock", CX + 18, y + 18, C["brandA"], 0.6))
        out.append(text(CX + 32, y + 22, "AI Context Used", 11, C["txt"], 650))
        for i, ln in enumerate(["Garden memories", "Past conversations", "Relationship tone"]):
            out.append(f'<path d="M{CX+18} {y+38+i*13} l{2.4} {2.6} {4.4} -{5}" fill="none" stroke="{C["green"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')
            out.append(text(CX + 32, y + 42 + i * 13, ln, 10, C["t2"], 500))
        out.append(text(CX + CW - 14, y + 22, "Why this response?", 9.5, C["brandA"], 700, "end"))
        y += 90
        out.append(rrect(CX, y, CW, 38, 12, "#0d0a24", C["line"], 1))
        out.append(text(CX + 14, y + 24, "Type a message…", 11, C["t3"]))
        out.append(f'<circle cx="{CX+CW-20}" cy="{y+19}" r="13" fill="url(#gBrand)"/>')
        out.append(text(CX + CW - 20, y + 24, "→", 14, "#fff", 800, "middle"))

    elif hero == "vault":
        cx0 = W / 2
        out.append(orb(cx0, y + 40, 32))
        out.append(icon("lock", cx0, y + 40, "rgba(255,255,255,0.95)", 1.5))
        y += 92
        rows = [("book", "brand", "Stories", "245 items"),
                ("mic", "pink", "Voice Notes", "38 items"),
                ("photo", "cyan", "Photos", "122 items"),
                ("chat", "amber", "Conversations", "1,024 items")]
        for ic, col, k, cnt in rows:
            out.append(rrect(CX, y, CW, 40, 12, "url(#gCard)", C["line"], 1))
            out.append(chip(CX + 8, y + 3, ic, ACCENT[col]))
            out.append(text(CX + 50, y + 25, k, 12, C["txt"], 600))
            out.append(text(CX + CW - 30, y + 25, cnt, 11, C["t2"], 500, "end"))
            out.append(text(CX + CW - 14, y + 25, "›", 15, C["t3"], 400, "end"))
            y += 48
        out.append(rrect(CX, y, CW, 44, 13, A(C["green"], 0.09), C["green"], 1))
        out.append(icon("shieldok", CX + 24, y + 22, C["green"], 0.8))
        out.append(text(CX + 44, y + 19, "Storage: LOCAL VAULT", 11, C["txt"], 650))
        out.append(text(CX + 44, y + 33, "AES-256-GCM Protected", 10, C["green"], 500))
        y += 54
        out.append(button(CX, y, CW, "Export Everything", "brand", 40))
        out.append(button(CX, y + 48, CW, "Delete Everything", "danger", 40))

    elif hero == "relationships":
        rows = [("D", C["brandA"], "David (You)", "Owner", "You", "brand"),
                ("S", C["amber"], "Sarah", "Daughter", "Supportive", "good"),
                ("J", C["cyan"], "John", "Friend", "Casual", "info"),
                ("E", C["pink"], "Dr. Emily", "Therapist", "Professional", "gold"),
                ("M", C["green"], "Mom", "Family", "Warm", "warn")]
        for init, col, name, rel, tl, tone in rows:
            s, y = person_row(y, init, col, name, rel, tl, tone)
            out.append(s)
        out.append(button(CX, y + 2, CW, "+  Add Relationship", "brand", 42))

    elif hero == "addrel":
        out.append(text(CX, y, "Relationship Type", 12, C["txt"], 700))
        y += 12
        chips = ["Parent", "Child", "Friend", "Partner", "Customer", "Stranger", "Other"]
        cxp = CX
        for i, lbl in enumerate(chips):
            wch = 14 + len(lbl) * 6.6
            if cxp + wch > CX + CW:
                cxp = CX
                y += 34
            on = (lbl == "Friend")
            out.append(rrect(cxp, y, wch, 28, 9, "url(#gBrand)" if on else "rgba(255,255,255,0.05)",
                             None if on else C["line"], 1))
            out.append(text(cxp + wch / 2, y + 18, lbl, 11, "#fff" if on else C["t2"], 600, "middle"))
            cxp += wch + 8
        y += 44
        out.append(text(CX, y, "Nickname (Optional)", 12, C["txt"], 700))
        out.append(rrect(CX, y + 8, CW, 36, 11, "#0d0a24", C["line"], 1))
        out.append(text(CX + 14, y + 31, "Best friend", 11.5, C["txt"], 500))
        y += 58
        out.append(text(CX, y, "Conversation Style", 12, C["txt"], 700))
        y += 12
        styles = [("Friendly", True), ("Professional", False), ("Humorous", False), ("Formal", False)]
        for i, (lbl, on) in enumerate(styles):
            gx = CX + (i % 2) * (CW / 2 + 4)
            gy = y + (i // 2) * 40
            out.append(rrect(gx, gy, CW / 2 - 4, 32, 10, "url(#gBrand)" if on else "rgba(255,255,255,0.05)",
                             None if on else C["line"], 1))
            out.append(text(gx + (CW / 2 - 4) / 2, gy + 20, lbl, 11.5, "#fff" if on else C["t2"], 600, "middle"))
        y += 88
        out.append(button(CX, y, CW, "Save Relationship", "brand", 42))

    elif hero == "health":
        bars = [("Identity Stability", 0.98, "98%", C["green"]),
                ("Memory Quality", 0.87, "87%", C["brandA"]),
                ("Engagement Average", 0.92, "92%", C["amber"]),
                ("Moderation Pass Rate", 0.994, "99.4%", C["cyan"])]
        for lbl, pct, val, col in bars:
            s, y = statbar(y, lbl, pct, val, col)
            out.append(s)
        y += 4
        out.append(rrect(CX, y, CW, 46, 14, "url(#gCard)", C["line"], 1))
        out.append(icon("net", CX + 24, y + 23, C["brandA"], 0.9))
        out.append(text(CX + 46, y + 21, "Relationship Graph", 12, C["txt"], 600))
        out.append(text(CX + 46, y + 35, "connections", 10.5, C["t2"]))
        out.append(text(CX + CW - 14, y + 30, "34", 20, C["txt"], 800, "end"))
        y += 56
        out.append(rrect(CX, y, CW, 44, 14, A(C["brandA"], 0.08), C["brandA"], 1))
        out.append(text(CX + 14, y + 20, "Last Fine Tune", 11, C["t2"], 500))
        out.append(text(CX + 14, y + 35, "Today at 3:42 PM", 12, C["txt"], 650))
        out.append(text(CX + CW - 14, y + 28, "auto", 10, C["green"], 600, "end"))
        y += 54
        out.append(button(CX, y, CW, "Run Fine Tune", "brand", 42))

    elif hero == "marketplace":
        out.append(rrect(CX, y, CW, 34, 11, "#0d0a24", C["line"], 1))
        out.append(icon("search", CX + 18, y + 17, C["t3"], 0.75))
        out.append(text(CX + 34, y + 21, "Search profiles…", 11, C["t3"]))
        y += 44
        cats = ["All", "Health", "Finance", "Career", "Edu"]
        cxp = CX
        for i, lbl in enumerate(cats):
            wch = 14 + len(lbl) * 6.4
            on = (i == 0)
            out.append(rrect(cxp, y, wch, 24, 8, "url(#gBrand)" if on else "rgba(255,255,255,0.05)",
                             None if on else C["line"], 1))
            out.append(text(cxp + wch / 2, y + 16, lbl, 10, "#fff" if on else C["t2"], 600, "middle"))
            cxp += wch + 6
        y += 36
        cards = [("chart", "green", "Financial Expert AI", "Wealth advisor & planning", 4.9, "125"),
                 ("heart", "pink", "Wellness Coach", "Mental & physical health", 4.8, "98"),
                 ("star2", "amber", "Creator Assistant", "Brand & content expert", 4.9, "210"),
                 ("book", "cyan", "Historical Expert", "History & civilization", 4.7, "76")]
        for ic, col, k, s, rt, cnt in cards:
            out.append(rrect(CX, y, CW, 56, 14, "url(#gCard)", C["line"], 1))
            out.append(f'<circle cx="{CX+28}" cy="{y+28}" r="18" fill="{A(ACCENT[col],0.18)}" stroke="{ACCENT[col]}" stroke-width="1.2"/>')
            out.append(icon(ic, CX + 28, y + 28, ACCENT[col], 0.95))
            out.append(text(CX + 56, y + 22, k, 12.5, C["txt"], 650))
            out.append(text(CX + 56, y + 37, s, 10, C["t2"]))
            out.append(stars(CX + 56, y + 49, rt, C["gold"], 0.62))
            out.append(text(CX + 96, y + 51, f"{rt}", 9.5, C["gold"], 700))
            out.append(text(CX + CW - 14, y + 51, f"▲ {cnt}", 9.5, C["t3"], 600, "end"))
            y += 64

    elif hero == "licensing":
        out.append(text(CX, y, "Available Licenses", 12.5, C["txt"], 700))
        y += 14
        lic = [("chat", "brand", "Consult", "$20 / session", "One-on-one expertise"),
               ("sliders", "amber", "Fine Tune", "$499 / license", "Use for training"),
               ("people", "pink", "Clone Agent", "Negotiated", "Create derivative agents")]
        for ic, col, k, price, s in lic:
            out.append(rrect(CX, y, CW, 56, 14, "url(#gCard)", C["line"], 1))
            out.append(chip(CX + 12, y + 11, ic, ACCENT[col]))
            out.append(text(CX + 56, y + 24, k, 13, C["txt"], 700))
            out.append(text(CX + 56, y + 40, s, 10, C["t2"]))
            out.append(text(CX + CW - 14, y + 26, price, 12, ACCENT[col], 700, "end"))
            out.append(text(CX + CW - 14, y + 42, "›", 15, C["t3"], 400, "end"))
            y += 64
        out.append(rrect(CX, y, CW, 48, 14, A(C["green"], 0.08), C["green"], 1))
        out.append(text(CX + 14, y + 20, "Derivative Rights", 12, C["txt"], 650))
        out.append(text(CX + 14, y + 36, "Allow others to create from this profile", 9.5, C["t2"]))
        out.append(toggle(CX + CW - 44, y + 14, True))
        y += 58
        out.append(button(CX, y, CW, "Manage Licenses & Grants", "brand", 42))

    elif hero == "embodiments":
        rows = [("phone", "brand", "iPhone", "on", "ONLINE"),
                ("watch", "cyan", "Apple Watch", "on", "ONLINE"),
                ("headset", "pink", "AR Headset", "off", "OFFLINE"),
                ("robot", "amber", "Robot", "avail", "AVAILABLE"),
                ("speaker", "green", "Smart Speaker", "on", "ONLINE")]
        for ic, col, k, tone, lbl in rows:
            out.append(rrect(CX, y, CW, 46, 13, "url(#gCard)", C["line"], 1))
            out.append(chip(CX + 10, y + 6, ic, ACCENT[col]))
            out.append(text(CX + 54, y + 28, k, 12.5, C["txt"], 600))
            out.append(status_dot(CX + CW - 14, y + 23, lbl, tone))
            y += 54
        out.append(rrect(CX, y, CW, 52, 14, A(C["brandA"], 0.08), C["brandA"], 1))
        out.append(icon("finger", CX + 26, y + 26, C["brandA"], 1.1))
        out.append(text(CX + 52, y + 24, "Identity Signature", 11.5, C["txt"], 650))
        out.append(text(CX + 52, y + 39, "Consistent across all forms", 9.5, C["t2"]))
        out.append(text(CX + CW - 14, y + 32, "98.9%", 17, C["green"], 800, "end"))

    elif hero == "control":
        out.append(text(CX, y, "Privacy", 12, C["t2"], 700, spacing=0.4))
        y += 10
        priv = [("Offline Mode", "on", True), ("Soft Contribution", "off", False),
                ("Data Sharing", "none", None)]
        for k, val, on in priv:
            out.append(rrect(CX, y, CW, 42, 12, "url(#gCard)", C["line"], 1))
            out.append(text(CX + 16, y + 26, k, 12, C["txt"], 600))
            if on is None:
                out.append(text(CX + CW - 16, y + 26, "None", 11, C["t2"], 600, "end"))
            else:
                out.append(toggle(CX + CW - 44, y + 11, on))
            y += 50
        out.append(text(CX, y, "Permissions", 12, C["t2"], 700, spacing=0.4))
        y += 10
        perms = [("mic", "Microphone", True), ("eye", "Camera", True), ("compass", "Location", False)]
        for ic, k, on in perms:
            out.append(rrect(CX, y, CW, 42, 12, "url(#gCard)", C["line"], 1))
            out.append(icon(ic, CX + 22, y + 21, C["brandA"], 0.72))
            out.append(text(CX + 40, y + 26, k, 12, C["txt"], 600))
            out.append(toggle(CX + CW - 44, y + 11, on))
            y += 50
        y += 2
        out.append(button(CX, y, (CW - 10) / 2, "Export My Data", "brand", 40))
        out.append(button(CX + (CW - 10) / 2 + 10, y, (CW - 10) / 2, "Delete Profile", "danger", 40))

    elif hero == "design":
        out.append(text(CX, y, "Colors", 12, C["txt"], 700))
        y += 12
        cols = [("#7B5CFF", "Neon Purple"), ("#FFB84D", "Warm Amber"),
                ("#1A1333", "Deep Indigo"), ("#C7C9D9", "Soft Silver")]
        for i, (hexc, name) in enumerate(cols):
            gx = CX + (i % 2) * (CW / 2 + 6)
            gy = y + (i // 2) * 44
            out.append(rrect(gx, gy, CW / 2 - 6, 36, 10, "url(#gCard)", C["line"], 1))
            out.append(rrect(gx + 8, gy + 8, 20, 20, 6, hexc, C["line"], 1))
            out.append(text(gx + 36, gy + 17, name, 9.5, C["txt"], 600))
            out.append(text(gx + 36, gy + 29, hexc, 8.5, C["t2"], 500, mono=True))
        y += 100
        out.append(text(CX, y, "Typography", 12, C["txt"], 700))
        y += 12
        out.append(rrect(CX, y, CW, 52, 12, "url(#gCard)", C["line"], 1))
        out.append(text(CX + 14, y + 30, "Aa", 26, C["txt"], 750))
        out.append(text(CX + 58, y + 24, "SF Pro Display", 12, C["txt"], 650))
        out.append(text(CX + 58, y + 39, "Native system type · tabular numerals", 9.5, C["t2"]))
        y += 62
        out.append(text(CX, y, "UI Style", 12, C["txt"], 700))
        y += 12
        for lbl, ic in [("Liquid glass · floating cards", "grid"),
                        ("Haptic interactions", "bolt"),
                        ("AI transparency", "eye"),
                        ("Apple Human Interface", "phone")]:
            out.append(rrect(CX, y, CW, 34, 10, "url(#gCard)", C["line"], 1))
            out.append(icon(ic, CX + 20, y + 17, C["brandA"], 0.62))
            out.append(text(CX + 38, y + 21, lbl, 11, C["txt"], 550))
            y += 40

    elif hero == "genesis":
        out.append(orb(W / 2, y + 34, 26))
        out.append(text(W / 2, y + 78, "Four questions to birth your AI", 12, C["txt"], 600, "middle"))
        y += 100
        # The four fields `GenesisAnswers` actually takes — social_style,
        # humor, comfort, what_matters — rather than four questions written
        # for the mock. Two of those had drifted from the model *and* ran off
        # the side of the phone.
        qs = [("1", "How are you around people?", "answered"),
              ("2", "What makes you laugh?", "answered"),
              ("3", "How do you comfort a friend?", "now"),
              ("4", "What matters most to you?", "next")]
        for n, q, state in qs:
            col = C["green"] if state == "answered" else (C["brandA"] if state == "now" else C["t3"])
            out.append(rrect(CX, y, CW, 46, 13, "url(#gCard)", C["line"],
                             1) if state != "now" else rrect(CX, y, CW, 46, 13, A(C["brandA"], 0.10), C["brandA"], 1.4))
            out.append(f'<circle cx="{CX+24}" cy="{y+23}" r="12" fill="{A(col,0.18)}" stroke="{col}" stroke-width="1.3"/>')
            if state == "answered":
                out.append(f'<path d="M{CX+19} {y+23} l{3} {3.4} {6} -{6.6}" fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
            else:
                out.append(text(CX + 24, y + 27, n, 12, col, 800, "middle"))
            out.append(text(CX + 46, y + 27, q, 11, C["txt"] if state != "next" else C["t3"], 600))
            y += 54
        out.append(text(W / 2, y + 4, "Omit a name and it chooses its own", 9.5, C["t3"], 500, "middle"))

    elif hero == "beacon":
        qs_ = 116
        qx, qy = W / 2 - qs_ / 2, y
        out.append(qr(qx, qy, qs_))
        # centered handle badge
        out.append(f'<circle cx="{W/2}" cy="{qy+qs_/2}" r="18" fill="{C["scrB"]}" stroke="{C["brandA"]}" stroke-width="2"/>')
        out.append(icon("person", W / 2, qy + qs_ / 2, C["brandA"], 1.0))
        y = qy + qs_ + 18
        out.append(text(W / 2, y, "@your.handle", 14, C["brandA"], 700, "middle"))
        out.append(text(W / 2, y + 16, "Scan to summon this profile — anywhere", 10, C["t2"], 500, "middle"))
        y += 34
        for ic, col, k, s in [("target", "brand", "@handle · #tag · beacon", "one resolver, three refs"),
                              ("chart", "amber", "Scans counted", "247 summons · pick it back up"),
                              ("dove", "cyan", "Departed → memorial", "a beacon outlives the profile")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)

    elif hero == "objection":
        out.append(rrect(CX, y, CW, 58, 15, A(C["amber"], 0.10), C["amber"], 1.2))
        out.append(icon("flag", CX + 26, y + 29, C["amber"], 1.1))
        out.append(text(CX + 52, y + 24, "Profile restricted", 13, C["txt"], 700))
        out.append(text(CX + 52, y + 40, "An objection is under review", 10.5, C["t2"]))
        y += 70
        steps = [("green", "active", "Live and discoverable", True),
                 ("amber", "restricted", "Objection pending · hidden", True),
                 ("red", "terminated", "Content erased · tombstone", False),
                 ("cyan", "departed", "Memorial, preserved", False)]
        lx = CX + 16
        out.append(f'<line x1="{lx}" y1="{y+8}" x2="{lx}" y2="{y+8+len(steps)*54-38}" stroke="{C["line"]}" stroke-width="2"/>')
        for col, k, s, done in steps:
            c = ACCENT[col]
            out.append(f'<circle cx="{lx}" cy="{y+12}" r="8" fill="{c if k in ("active","restricted") else C["scrB"]}" stroke="{c}" stroke-width="2"/>')
            out.append(rrect(lx + 20, y - 4, CW - 36, 40, 11, "url(#gCard)", C["line"], 1))
            out.append(text(lx + 34, y + 12, k, 11.5, C["txt"], 700))
            out.append(text(lx + 34, y + 26, s, 9.5, C["t2"]))
            y += 54

    elif hero == "cloud":
        out.append(rrect(CX, y, CW, 58, 15, "url(#gCard)", C["line"], 1))
        out.append(icon("cloud", CX + 28, y + 28, C["brandA"], 1.3))
        out.append(text(CX + 56, y + 24, "Contribute to the model", 12.5, C["txt"], 650))
        out.append(text(CX + 56, y + 40, "Preview exactly what would leave", 10, C["t2"]))
        out.append(toggle(CX + CW - 44, y + 20, False))
        y += 70
        out.append(text(CX, y, "Next contribution preview", 11, C["t2"], 600))
        y += 8
        out.append(rrect(CX, y, CW, 74, 13, "#0d0a24", C["line"], 1))
        out.append(text(CX + 14, y + 22, "ref: a7f3…  (id stripped)", 10, C["cyan"], 500, mono=True))
        out.append(text(CX + 14, y + 40, "\"How do you stay patient?\"", 10, C["txt"], 500))
        out.append(text(CX + 14, y + 56, "→ name replaced · rated +1 · revocable", 9.5, C["t3"], 500))
        y += 86
        for ic, col, k, s in [("eye", "cyan", "Anonymized at gateway", "no ids, names replaced"),
                              ("warn", "red", "Revoke deletes items", "erased by their refs")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)

    elif hero == "offline":
        out.append(orb(W / 2, y + 40, 32))
        out.append(icon("shieldok", W / 2, y + 40, "rgba(255,255,255,0.95)", 1.7))
        y += 88
        out.append(text(W / 2, y, "Nothing leaves this device", 14, "#fff", 700, "middle"))
        out.append(text(W / 2, y + 18, "QRME_OFFLINE=1 · a hard guarantee", 10.5, C["t2"], 500, "middle"))
        y += 40
        for ic, col, k, s, pt in [("cloud", "red", "Model API calls", "none outbound", ("BLOCKED", "crit")),
                                  ("link", "red", "Cloud gateway", "bypassed even if set", ("BLOCKED", "crit")),
                                  ("sliders", "green", "Inference & tune", "recomputed on-host", ("LOCAL", "good")),
                                  ("eye", "cyan", "GET /offline", "proves the posture", ("PROVEN", "info"))]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "pill": pt, "h": 48})
            out.append(s2)

    elif hero == "memorial":
        out.append(orb(W / 2, y + 38, 30))
        out.append(icon("dove", W / 2, y + 38, "rgba(255,255,255,0.95)", 1.6))
        y += 82
        out.append(text(W / 2, y, "AI assistant", 20, "#fff", 750, "middle"))
        out.append(text(W / 2, y + 18, "@your.handle · a memorial", 10.5, C["t2"], 500, "middle"))
        y += 40
        for ic, col, k, s in [("dove", "cyan", "Graceful departure", "a farewell for every relationship"),
                              ("lock", "green", "Memory preserved", "sealed in the vault, exportable"),
                              ("people", "amber", "Succession", "ownership passes, token revoked"),
                              ("chat", "brand", "Chat closes with 410", "a goodbye, never a silent 404")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)

    elif hero == "moderation":
        out.append(rrect(CX, y, CW, 64, 16, "url(#gCard)", C["line"], 1))
        out.append(icon("chat", CX + 22, y + 22, C["brandA"], 0.8))
        out.append(text(CX + 40, y + 20, "Your assistant wants to reply", 11, C["t2"], 600))
        out.append(pill(CX + CW - 14, y + 20, "HELD", "warn"))
        out.append(text(CX + 14, y + 44, "“Tell me about your rose garden.”", 11.5, C["txt"], 500))
        y += 76
        bw = (CW - 12) / 2
        out.append(rrect(CX, y, bw, 60, 15, A(C["green"], 0.10), C["green"], 1.4))
        out.append(icon("shieldok", CX + bw / 2, y + 24, C["green"], 1.1))
        out.append(text(CX + bw / 2, y + 48, "Approve", 12, C["green"], 700, "middle"))
        out.append(rrect(CX + bw + 12, y, bw, 60, 15, A(C["red"], 0.10), C["red"], 1.4))
        out.append(icon("warn", CX + bw + 12 + bw / 2, y + 24, C["red"], 1.1))
        out.append(text(CX + bw + 12 + bw / 2, y + 48, "Reject", 12, C["red"], 700, "middle"))
        y += 74
        for ic, col, k, s, pt in [("list", "amber", "Approval queue", "manual mode holds every reply", ("3", "warn")),
                                  ("shieldok", "green", "Public posts → strict", "always the strict filter", None)]:
            c = {"icon": ic, "color": col, "k": k, "s": s, "h": 48}
            if pt:
                c["pill"] = pt
            s2, y = card_block(y, c)
            out.append(s2)

    elif hero == "embedding":
        dims = [("Engagement", 0.82, C["brandA"]), ("Warmth", 0.74, C["amber"]),
                ("Depth", 0.60, C["cyan"]), ("Positivity", 0.70, C["green"]),
                ("Stress", 0.35, C["red"]), ("Continuity", 0.90, C["pink"])]
        for lbl, v, col in dims:
            s, y = statbar(y, lbl, v, f"{v:.2f}", col)
            out.append(s)
        y += 4
        out.append(rrect(CX, y, CW, 50, 14, A(C["brandA"], 0.08), C["brandA"], 1))
        out.append(icon("bolt", CX + 24, y + 25, C["brandA"], 0.9))
        out.append(text(CX + 46, y + 22, "EMA-updated every interaction", 11, C["txt"], 600))
        out.append(text(CX + 46, y + 37, "versioned · conditions attention weighting", 9.5, C["t2"]))

    elif hero == "modal":
        seg = ["Text", "Voice", "Image", "Video"]
        out.append(rrect(CX, y, CW, 38, 12, "#0d0a24", C["line"], 1))
        sw = (CW - 8) / 4
        for i, lbl in enumerate(seg):
            on = (i == 1)
            if on:
                out.append(rrect(CX + 4 + i * sw, y + 4, sw, 30, 9, "url(#gBrand)"))
            out.append(text(CX + 4 + i * sw + sw / 2, y + 24, lbl, 11, "#fff" if on else C["t2"], 650, "middle"))
        y += 50
        out.append(rrect(CX, y, CW, 60, 15, "url(#gCard)", C["line"], 1))
        out.append(icon("mic", CX + 26, y + 30, C["pink"], 1.2))
        out.append(text(CX + 52, y + 26, "Voice reply", 12.5, C["txt"], 650))
        out.append(text(CX + 52, y + 42, "preserved from your voice-note sources", 9.5, C["t2"]))
        out.append(pill(CX + CW - 14, y + 24, "PRESERVED", "good"))
        y += 72
        for ic, col, k, s in [("photo", "cyan", "Image & video", "a render descriptor on the reply"),
                              ("shieldok", "green", "Same identity, any form", "persona signature is invariant")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)

    elif hero == "signin":
        out.append(orb(W / 2, y + 44, 36))
        out.append(icon("person", W / 2, y + 42, "rgba(255,255,255,0.92)", 1.5))
        y += 106
        out.append(text(W / 2, y, "Welcome back, David", 16, "#fff", 750, "middle"))
        out.append(text(W / 2, y + 20, "Your vault is encrypted and local", 11, C["t2"], 400, "middle"))
        y += 44
        out.append(rrect(CX, y, CW, 56, 15, "url(#gCard)", C["line"], 1))
        out.append(icon("finger", CX + 30, y + 28, C["brandA"], 1.2))
        out.append(text(CX + 58, y + 24, "Unlock with Face ID", 12.5, C["txt"], 650))
        out.append(text(CX + 58, y + 40, "or your vault passphrase", 10, C["t2"]))
        y += 72
        out.append(button(CX, y, CW, "Sign In", "brand", 44))
        out.append(button(CX, y + 54, CW, "Use a different profile", "ghost", 42))

    elif hero == "endsession":
        out.append(orb(W / 2, y + 40, 32))
        out.append(icon("lock", W / 2, y + 40, "rgba(255,255,255,0.95)", 1.4))
        y += 92
        out.append(text(W / 2, y, "Session ended", 16, "#fff", 750, "middle"))
        out.append(text(W / 2, y + 20, "Your vault is sealed. See you soon.", 11, C["t2"], 400, "middle"))
        y += 42
        for ic, col, k, s in [("chat", "brand", "Conversation", "12 messages this session"),
                              ("lock", "green", "Memories saved & sealed", "AES-256-GCM, on device"),
                              ("eye", "cyan", "Nothing left your vault", "offline the whole time")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)
        out.append(button(CX, y + 2, CW, "Sign Out", "brand", 42))

    elif hero == "auth":
        out.append(orb(W / 2, y + 36, 30, head_profile=True))
        y += 82
        out.append(text(W / 2, y, "Create your account", 17, "#fff", 750, "middle", -0.3))
        out.append(text(W / 2, y + 20, "One login for QRME, JIM-mini & PDI", 11, C["t2"], 400, "middle"))
        y += 42
        out.append(rrect(CX, y, CW, 46, 13, "#ffffff"))
        out.append(apple_mark(CX + 30, y + 12))
        out.append(text(W / 2 + 10, y + 28, "Continue with Apple", 13, "#0b0b0f", 650, "middle"))
        y += 54
        out.append(rrect(CX, y, CW, 46, 13, "#ffffff"))
        out.append(google_mark(CX + 31, y + 15))
        out.append(text(W / 2 + 10, y + 28, "Continue with Google", 13, "#1f1f1f", 650, "middle"))
        y += 54
        out.append(rrect(CX, y, CW, 46, 13, "rgba(255,255,255,0.06)", C["line"], 1))
        out.append(envelope(CX + 41, y + 23, C["brandA"]))
        out.append(text(W / 2 + 10, y + 28, "Continue with Email", 13, C["txt"], 650, "middle"))
        y += 62
        out.append(text(W / 2, y, "Age & identity are verified in the next step.", 9.5, C["t3"], 500, "middle"))
        out.append(text(W / 2, y + 16, "By continuing you agree to the Terms & Privacy Policy.", 9, C["t3"], 500, "middle"))

    elif hero == "verify":
        out.append(orb(W / 2, y + 36, 28))
        out.append(icon("finger", W / 2, y + 34, "rgba(255,255,255,0.92)", 1.3))
        y += 78
        out.append(text(W / 2, y, "Verify it's really you", 16, "#fff", 750, "middle", -0.3))
        out.append(text(W / 2, y + 19, "Just once — it protects you and the people", 10.5, C["t2"], 400, "middle"))
        out.append(text(W / 2, y + 33, "who appear in your profiles.", 10.5, C["t2"], 400, "middle"))
        y += 52
        fs = 78
        fx = W / 2 - fs / 2
        out.append(rrect(fx, y, fs, fs, 18, A(C["brandA"], 0.06), C["brandA"], 1))
        for bx, by, dx, dy in [(fx + 12, y + 12, 1, 1), (fx + fs - 12, y + 12, -1, 1),
                               (fx + 12, y + fs - 12, 1, -1), (fx + fs - 12, y + fs - 12, -1, -1)]:
            out.append(f'<path d="M{bx} {by+13*dy} L{bx} {by} L{bx+13*dx} {by}" fill="none" '
                       f'stroke="{C["brandA"]}" stroke-width="2" stroke-linecap="round"/>')
        out.append(icon("person", W / 2, y + fs / 2, C["brandA"], 1.7))
        y += fs + 14
        for ic, col, k, s, badge, tone in [
                ("shieldok", "green", "Age 18+", "unlocks adult profiles", "VERIFIED", "good"),
                ("finger", "brand", "Face ID liveness", "a real, present person", "PASSED", "good"),
                ("doc", "cyan", "Government ID", "unlocks third-party use", "OPTIONAL", "info")]:
            out.append(rrect(CX, y, CW, 50, 14, "url(#gCard)", C["line"], 1))
            out.append(chip(CX + 10, y + 8, ic, ACCENT[col]))
            out.append(text(CX + 54, y + 21, k, 12.5, C["txt"], 650))
            out.append(text(CX + 54, y + 36, s, 10, C["t2"]))
            out.append(pill(CX + CW - 14, y + 25, badge, tone))
            y += 58
        out.append(button(CX, y + 2, CW, "Continue", "brand", 44))

    elif hero == "permissions":
        out.append(text(CX, y, "Adjust any of these anytime in Settings.", 10.5, C["t2"]))
        y += 28
        rows = [("info", "brand", "Notifications", "check-ins & summons", "on"),
                ("photo", "cyan", "Camera & Mic", "live video & AR/VR", "on"),
                ("heart", "red", "Health & Motion", "the JIM-mini tandem", "avail"),
                ("people", "amber", "Contacts", "map to relationships", "off")]
        for ic, col, k, s, st in rows:
            out.append(rrect(CX, y, CW, 56, 15, "url(#gCard)", C["line"], 1))
            out.append(chip(CX + 12, y + 11, ic, ACCENT[col]))
            out.append(text(CX + 58, y + 24, k, 12.5, C["txt"], 650))
            out.append(text(CX + 58, y + 40, s, 10.5, C["t2"]))
            on = st == "on"
            tx = CX + CW - 48
            out.append(rrect(tx, y + 18, 40, 22, 11, C["green"] if on else "#0d0a24", C["line"] if not on else None, 1))
            out.append(f'<circle cx="{tx + (28 if on else 12)}" cy="{y+29}" r="8.5" fill="#fff"/>')
            y += 64
        out.append(button(CX, y + 2, CW, "Continue", "brand", 44))

    elif hero == "avatar":
        out.append(text(CX, y, "A 2D portrait for chat, a 3D avatar for AR & VR.", 10.5, C["t2"]))
        y += 26
        gw = (CW - 12) / 2
        # 2D portrait tile
        out.append(rrect(CX, y, gw, 128, 16, "url(#gCard)", C["line"], 1))
        out.append(face(CX + gw / 2, y + 54, 64, _assistant_face()))
        out.append(icon("person", CX + gw / 2, y + 52, "rgba(255,255,255,0.92)", 1.4))
        out.append(pill(CX + gw - 12, y + 20, "2D", "brand"))
        out.append(text(CX + gw / 2, y + 104, "Portrait", 11.5, C["txt"], 650, "middle"))
        out.append(text(CX + gw / 2, y + 118, "chat & feed", 9.5, C["t2"], 400, "middle"))
        # 3D avatar tile
        gx = CX + gw + 12
        out.append(rrect(gx, y, gw, 128, 16, "url(#gCard)", C["line"], 1))
        out.append(ring(gx + gw / 2, y + 54, 30, 0.75, C["cyan"], 4))
        out.append(face(gx + gw / 2, y + 54, 54, _assistant_face()))
        out.append(icon("person", gx + gw / 2, y + 52, "rgba(255,255,255,0.92)", 1.2))
        out.append(pill(gx + gw - 12, y + 20, "3D", "info"))
        out.append(text(gx + gw / 2, y + 104, "Avatar", 11.5, C["txt"], 650, "middle"))
        out.append(text(gx + gw / 2, y + 118, "video · AR · VR", 9.5, C["t2"], 400, "middle"))
        y += 142
        out.append(text(CX, y, "Style", 12, C["txt"], 700))
        y += 14
        seg = ["Realistic", "Stylized", "Abstract"]
        out.append(rrect(CX, y, CW, 38, 12, "#0d0a24", C["line"], 1))
        sw = (CW - 8) / 3
        for i, lbl in enumerate(seg):
            on = i == 1
            if on:
                out.append(rrect(CX + 4 + i * sw, y + 4, sw, 30, 9, "url(#gBrand)"))
            out.append(text(CX + 4 + i * sw + sw / 2, y + 24, lbl, 11.5, "#fff" if on else C["t2"], 650, "middle"))
        y += 48
        out.append(button(CX, y, CW, "Generate from my photos", "brand", 44))

    elif hero == "immersive":
        ph = 188
        out.append(rrect(CX, y, CW, ph, 18, "url(#gCard)", C["line"], 1))
        # perspective floor grid
        fy = y + ph - 20
        for i in range(-3, 4):
            out.append(f'<path d="M{W/2} {y+96} L{W/2 + i*70} {fy}" stroke="{A(C["cyan"],0.25)}" stroke-width="1"/>')
        for j, gy in enumerate([y + 120, y + 142, y + 166]):
            out.append(f'<line x1="{CX+14}" y1="{gy}" x2="{CX+CW-14}" y2="{gy}" stroke="{A(C["cyan"],0.18)}" stroke-width="1"/>')
        # avatar standing in the space
        out.append(orb(W / 2, y + 74, 26))
        out.append(icon("person", W / 2, y + 72, "rgba(255,255,255,0.95)", 1.3))
        out.append(f'<ellipse cx="{W/2}" cy="{y+128}" rx="34" ry="7" fill="{A(C["cyan"],0.18)}"/>')
        out.append(pill(CX + CW - 14, y + 22, "AR HEADSET · LINKED", "info"))
        out.append(icon("headset", CX + 28, y + 24, C["cyan"], 0.9))
        y += ph + 14
        for ic, col, k, s in [("headset", "cyan", "Room-scale presence", "Stands in your room"),
                              ("speaker", "brand", "Spatial audio", "her voice comes from there"),
                              ("eye", "pink", "Passthrough AR, full VR", "your living room, or her world")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)

    elif hero == "frontpage":
        cx0 = W / 2
        out.append(face(cx0, y + 40, 76, _assistant_face()))
        out.append(text(cx0, y + 96, CHARACTER, 19, "#fff", 750, "middle"))
        out.append(text(cx0, y + 113, CHARACTER_ROLE, 10.5, C["t2"], 500,
                        "middle"))
        # The rating, with its own count beside it: one five-star review and
        # two hundred are different facts, and an average alone hides which.
        out.append(stars(cx0 - 62, y + 130, 4, C["gold"], 0.7))
        out.append(text(cx0 + 6, y + 134, "4.0 · 37 reviews", 10, C["t2"],
                        600))
        y += 152
        # Skills, wrapped so a long list cannot run off the card.
        out.append(text(CX, y, "SKILLS", 9.5, C["t3"], 700, spacing=0.8))
        y += 12
        sx = CX
        for label in ("budgeting", "retirement", "fee-only", "debt"):
            w = 14 + len(label) * 5.6
            if sx + w > CX + CW:
                sx, y = CX, y + 24
            out.append(rrect(sx, y, w, 20, 10, A(C["brandA"], 0.14),
                             C["brandA"], 1))
            out.append(text(sx + w / 2, y + 14, label, 9.5, C["brandA"], 600,
                            "middle"))
            sx += w + 6
        y += 40

        # Experience, then what people who actually talked to it said. A hero
        # screen draws its own rows — the generic card stack is an `else` to
        # this branch, not something a hero gets as well.
        out.append(text(CX, y, "EXPERIENCE", 9.5, C["t3"], 700, spacing=0.8))
        y += 14
        for title_, sub in (("Fee-only financial planner", "Bell & Co · 1994–2024"),
                            ("Retirement counsellor", "County Credit Union · 1988–1994")):
            out.append(rrect(CX, y, CW, 40, 12, "url(#gCard)", C["line"], 1))
            out.append(text(CX + 12, y + 17, title_, 10.5, C["txt"], 650))
            out.append(text(CX + 12, y + 30, sub, 9, C["t2"]))
            y += 46
        y += 4

        out.append(text(CX, y, "REVIEWS", 9.5, C["t3"], 700, spacing=0.8))
        out.append(text(CX + CW, y, "from people who talked to it", 8.5,
                        C["t3"], 500, "end"))
        y += 14
        out.append(rrect(CX, y, CW, 46, 12, "url(#gCard)", C["line"], 1))
        out.append(stars(CX + 12, y + 16, 5, C["gold"], 0.6))
        out.append(text(CX + 78, y + 19, "R. Okafor", 9, C["t2"], 600))
        out.append(text(CX + 12, y + 35, "\u201cExplained my pension plainly.\u201d",
                        10, C["txt"], 500))
        y += 56

        out.append(button(CX, y, CW, "Talk to Marcus", "brand", 40))

    elif hero == "video":
        vh = 196
        out.append(rrect(CX, y, CW, vh, 18, "url(#orb)", C["line"], 1))
        out.append(rrect(CX, y, CW, vh, 18, "url(#glow)"))
        out.append(face(W / 2, y + vh / 2 - 12, 96, _assistant_face()))
        out.append(icon("person", W / 2, y + vh / 2 - 14, "rgba(255,255,255,0.95)", 1.9))
        # LIVE badge
        out.append(rrect(CX + 14, y + 14, 58, 20, 10, A(C["red"], 0.9)))
        out.append(f'<circle cx="{CX+26}" cy="{y+24}" r="3.5" fill="#fff"/>')
        out.append(text(CX + 34, y + 28, "LIVE", 10.5, "#fff", 750))
        out.append(text(CX + 14, y + vh - 26, CHARACTER, 13, "#fff", 700))
        out.append(text(CX + 14, y + vh - 12, "1080p · end-to-end encrypted", 9.5, "rgba(255,255,255,0.75)"))
        # self preview tile
        out.append(rrect(CX + CW - 68, y + vh - 86, 56, 74, 12, "#0d0a24", "rgba(255,255,255,0.18)", 1))
        out.append(icon("person", CX + CW - 40, y + vh - 52, C["t2"], 1.2))
        out.append(text(CX + CW - 40, y + vh - 20, "You", 9, C["t2"], 600, "middle"))
        y += vh + 16
        # controls
        ctrls = [("mic", "ghost", C["txt"]), ("photo", "ghost", C["txt"]),
                 ("speaker", "ghost", C["txt"]), ("phone", "danger", C["red"])]
        n = len(ctrls)
        gap = 16
        d = 52
        total = n * d + (n - 1) * gap
        sx = W / 2 - total / 2
        for i, (ic, kind, icol) in enumerate(ctrls):
            bx = sx + i * (d + gap)
            fill = A(C["red"], 0.16) if kind == "danger" else "rgba(255,255,255,0.06)"
            stroke = C["red"] if kind == "danger" else C["line"]
            out.append(f'<circle cx="{bx+d/2}" cy="{y+d/2}" r="{d/2}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
            out.append(icon(ic, bx + d / 2, y + d / 2, icol, 1.2))
        y += d + 14
        out.append(text(W / 2, y, "Camera & mic stay on your device · encrypted stream", 9.3, C["t3"], 500, "middle"))

    elif hero == "allset":
        out.append(orb(W / 2, y + 40, 34))
        out.append(f'<path d="M{W/2-11} {y+40} l7 8 14 -16" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
        y += 100
        out.append(text(W / 2, y, "You're all set", 18, "#fff", 750, "middle", -0.3))
        out.append(text(W / 2, y + 21, "Ready to meet the world.", 11, C["t2"], 400, "middle"))
        y += 44
        for ic, col, k, s in [("person", "brand", "Profile created", "an AI version of you"),
                              ("db", "cyan", "Sources added", "1,024 memories, sealed"),
                              ("sliders", "amber", "Personality set", "warm · balanced boundaries"),
                              ("mask", "pink", "Avatar ready", "2D portrait + 3D for video & VR")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)
        out.append(button(CX, y + 2, CW, "Start chatting", "brand", 44))

    elif hero == "social":
        out.append(text(CX, y, "Collect to build the profile · publish to run it.",
                        10.5, C["t2"]))
        y += 24
        # the connected-platform palette (the set the suite connects to)
        dots = ["#E1306C", "#1DA1F2", "#25F4EE", "#1877F2", "#0A66C2", "#FF0000",
                "#FF4500", "#c9c9d6", "#25D366", "#0866FF", "#6364FF", "#9146FF",
                "#FFFC00", "#E2231A", "#E60023", "#5865F2"]
        dx = CX
        for col in dots:
            out.append(f'<circle cx="{dx+7:.1f}" cy="{y+4}" r="6.5" fill="{col}"/>')
            dx += 14.6
        out.append(text(CX, y + 22, "16 platforms — Instagram to Discord", 9, C["t3"], 500))
        y += 34
        out.append(text(CX, y, "COLLECTING", 9.5, C["t3"], 700, "start", 0.8))
        out.append(pill(CX + CW, y + 3, "→ builds profile", "info"))
        y += 16
        for ic, col, name, sub in [
                ("photo", "pink", "Instagram", "@dana.grows · 1,204 posts"),
                ("chat", "cyan", "X", "@dana · 820 posts")]:
            out.append(rrect(CX, y, CW, 50, 14, "url(#gCard)", C["line"], 1))
            out.append(chip(CX + 10, y + 8, ic, C[col]))
            out.append(text(CX + 54, y + 22, name, 12.5, C["txt"], 650))
            out.append(text(CX + 54, y + 37, sub, 10, C["t2"]))
            out.append(pill(CX + CW - 12, y + 25, "COLLECT", "info"))
            y += 58
        y += 6
        out.append(text(CX, y, "PUBLISHING", 9.5, C["t3"], 700, "start", 0.8))
        out.append(pill(CX + CW, y + 3, "runs on platform", "good"))
        y += 16
        ph = 82
        out.append(rrect(CX, y, CW, ph, 15, "url(#gCard)", C["line"], 1))
        out.append(chip(CX + 12, y + 12, "star2", C["brandA"]))
        out.append(text(CX + 54, y + 26, "TikTok", 12.5, C["txt"], 650))
        out.append(text(CX + 54, y + 42, "@dana.grows", 10, C["t2"]))
        out.append(status_dot(CX + 150, y + 30, "LIVE", "on"))
        out.append(text(CX + 54, y + 62, "scan to reach the profile", 9, C["t3"]))
        out.append(qr(CX + CW - 74, y + 10, 62, seed=11))
        y += ph + 10
        out.append(text(CX, y, "Posts are moderated · a QR beacon reaches you.",
                        9.5, C["t3"], 500))

    elif hero == "connectedapps":
        out.append(text(CX, y, "Your profile & agents, plugged into your apps.",
                        10.5, C["t2"]))
        y += 24
        provs = [
            ("Apple Intelligence", "#e7e7ef", "13 apps",
             "Photos · Calendar · Mail · Messages · +9"),
            ("Google Gemini", "#4285F4", "11 apps",
             "Photos · Gmail · Chrome · Maps · +7"),
            ("Microsoft Copilot", "#4cc2ff", "8 apps",
             "Photos · Explorer · 365 · Copilot · +4"),
            ("Canva Magic Studio", "#00c4cc", "8 tools",
             "Design · Media · Write · Edit · Layers · +3"),
        ]
        for name, col, count, sample in provs:
            out.append(rrect(CX, y, CW, 56, 15, "url(#gCard)", C["line"], 1))
            out.append(f'<circle cx="{CX+22}" cy="{y+28}" r="7" fill="{col}"/>')
            out.append(text(CX + 40, y + 24, name, 12.5, C["txt"], 700))
            out.append(pill(CX + CW - 12, y + 22, count, "info"))
            out.append(text(CX + 40, y + 40, sample, 9.5, C["t2"]))
            y += 64
        out.append(text(CX, y, "Collect context · act agentically · produce media.",
                        9.5, C["t3"], 500))

    elif hero == "excursions":
        out.append(text(CX, y, "Study a topic safely — your data stays home.",
                        10.5, C["t2"]))
        y += 24
        out.append(rrect(CX, y, CW, 56, 15, "url(#gCard)", C["line"], 1))
        out.append(chip(CX + 10, y + 11, "search", ACCENT["brand"]))
        out.append(text(CX + 54, y + 24, "Studying now", 12.5, C["txt"], 700))
        out.append(text(CX + 54, y + 40, "Managing arthritis", 10, C["t2"]))
        out.append(pill(CX + CW - 12, y + 24, "SANITIZED", "good"))
        y += 66
        out.append(text(CX, y, "OUTBOUND BRIEF", 9.5, C["t3"], 700, "start", 0.8))
        out.append(pill(CX + CW, y + 3, "2 redactions", "info"))
        y += 16
        out.append(rrect(CX, y, CW, 52, 15, "url(#gCard)", C["line"], 1))
        out.append(text(CX + 14, y + 22, "“help [private] with", 11, C["t2"], 500, mono=True))
        out.append(text(CX + 14, y + 38, "[private]’s arthritis”", 11, C["t2"], 500, mono=True))
        y += 62
        out.append(rrect(CX, y, CW, 44, 14, A(C["green"], 0.10), C["green"], 1))
        out.append(icon("shieldok", CX + 24, y + 22, C["green"], 0.8))
        out.append(text(CX + 44, y + 20, "Nothing left the host", 11, C["txt"], 650))
        out.append(text(CX + 44, y + 34, "local model only", 10, C["t2"]))
        y += 54
        out.append(text(CX, y, "Findings folded in as a knowledge source.",
                        9.5, C["t3"], 500))

    elif hero == "filesphotos":
        out.append(text(CX, y, "Bring in files & photos from your devices.",
                        10.5, C["t2"]))
        y += 26
        for name, ic in [("iOS", "phone"), ("Android", "phone"), ("Windows", "grid")]:
            out.append(rrect(CX, y, CW, 54, 14, "url(#gCard)", C["line"], 1))
            out.append(chip(CX + 12, y + 10, ic, C["brandA"]))
            out.append(text(CX + 56, y + 31, name, 13, C["txt"], 700))
            bx = CX + CW - 12
            for lab, col in [("Photos", C["cyan"]), ("Files", C["brandA"])]:
                w = 16 + len(lab) * 6.4
                out.append(rrect(bx - w, y + 16, w, 22, 11, A(col, 0.16), col, 1))
                out.append(text(bx - w / 2, y + 31, lab, 10, col, 700, "middle"))
                bx -= w + 8
            y += 62
        out.append(text(CX, y, "Only the folders & albums you pick — nothing else",
                        9.5, C["t3"], 500))

    elif hero == "assistant":
        prov = spec.get("provider", "apple")
        label, col, n, apps, caps = {
            "apple": ("Apple Intelligence", "#c9c9d6", 13,
                ["Photos","Calendar","Mail","Messages","Files","Notes","Reminders",
                 "Safari","Shortcuts","Passwords","Wallet","Phone","System"],
                [("Writing Tools","rewrite · proofread · summarize"),
                 ("Siri","cross-app actions & personal context"),
                 ("Visual Intelligence","analyze your screen & objects"),
                 ("Image Playground","Genmoji & image generation")]),
            "google": ("Google Gemini", "#4285F4", 11,
                ["Photos","Calendar","Gmail","Keep","Maps","Chrome","YouTube",
                 "Play","Gboard","Files","Live"],
                [("Ask Photos","natural-language photo search"),
                 ("Auto Browse","Chrome fills forms & books"),
                 ("Gemini Live","agentic multi-step actions"),
                 ("Workspace","Gmail summaries & smart replies")]),
            "microsoft": ("Microsoft Copilot", "#4cc2ff", 8,
                ["Photos","Explorer","Notepad","Paint","Snipping","Settings","365","Copilot"],
                [("Copilot Vision","real-time screen understanding"),
                 ("Recall","searchable memory of your screen"),
                 ("Click to Do","act on on-screen content"),
                 ("Microsoft 365","draft · analyze · present")]),
        }[prov]
        out.append(f'<circle cx="{CX+16}" cy="{y+8}" r="8" fill="{col}"/>')
        out.append(text(CX + 34, y + 13, label, 14, C["txt"], 750))
        out.append(pill(CX + CW, y + 9, f"{n} apps", "info"))
        y += 30
        out.append(text(CX, y, "APPS", 9, C["t3"], 700, "start", 0.6))
        y += 16
        bx = CX
        for a in apps:
            w = 14 + len(a) * 6.2
            if bx + w > CX + CW:
                bx = CX; y += 28
            out.append(rrect(bx, y, w, 22, 11, A(col, 0.14), col, 1))
            out.append(text(bx + w / 2, y + 15, a, 9.5, C["txt"], 600, "middle"))
            bx += w + 7
        y += 36
        out.append(text(CX, y, "CAPABILITIES", 9, C["t3"], 700, "start", 0.6))
        y += 16
        for k, s in caps:
            out.append(rrect(CX, y, CW, 40, 12, "url(#gCard)", C["line"], 1))
            out.append(f'<circle cx="{CX+18}" cy="{y+20}" r="4" fill="{col}"/>')
            out.append(text(CX + 34, y + 17, k, 12, C["txt"], 650))
            out.append(text(CX + 34, y + 31, s, 9.5, C["t2"]))
            y += 48

    elif hero == "objectionaudit":
        red = C.get("red", "#FF3B30")
        green = C.get("green", "#43E08A")
        amber = C.get("amber", "#F7B731")
        # Contested-state banner
        out.append(rrect(CX, y, CW, 30, 10, A(red, 0.12), red, 1))
        out.append(f'<circle cx="{CX+16}" cy="{y+15}" r="4" fill="{red}"/>')
        out.append(text(CX + 28, y + 19, "Restricted · under objection", 11,
                        red, 700))
        y += 42
        # Objection summary card
        out.append(rrect(CX, y, CW, 46, 12, "url(#gCard)", C["line"], 1))
        out.append(text(CX + 12, y + 18, "Objection obj_ab12", 11.5, C["txt"], 650))
        out.append(pill(CX + CW - 10, y + 10, "OPEN", "warn"))
        out.append(text(CX + 12, y + 35, "basis: subject_consent", 9.5, C["t2"]))
        y += 58
        # Timeline (vault-sealed)
        out.append(text(CX, y, "TIMELINE", 9, C["t3"], 700, "start", 0.6))
        out.append(text(CX + CW, y, "vault-sealed", 8.5, green, 600, "end"))
        y += 16
        for label, actor, dot in [("opened", "objector", green),
                                   ("reattested", "owner", green),
                                   ("awaiting review", "reviewer", amber)]:
            out.append(f'<circle cx="{CX+6}" cy="{y+8}" r="3" fill="{dot}"/>')
            out.append(text(CX + 18, y + 11, label, 10.5, C["txt"], 600))
            out.append(text(CX + CW, y + 11, actor, 9, C["t2"], 400, "end"))
            y += 22
        y += 8
        # Action rows per party
        out.append(text(CX, y, "ACTIONS", 9, C["t3"], 700, "start", 0.6))
        y += 16
        for title_, sub in [("Re-attest my basis", "owner · keep the profile"),
                            ("Uphold  ·  Dismiss", "reviewer · decide"),
                            ("Withdraw  ·  Revoke", "subject / estate · tear down")]:
            out.append(rrect(CX, y, CW, 38, 11, "url(#gCard)", C["line"], 1))
            out.append(text(CX + 12, y + 16, title_, 11, C["txt"], 650))
            out.append(text(CX + 12, y + 30, sub, 9, C["t2"]))
            y += 46

    else:  # generic stacked cards
        # `.get` rather than `[...]`: a screen whose body is agent groups has
        # no cards at all, and used to die here rather than render.
        for c in spec.get("cards", []):
            s, y = card_block(y, c)
            out.append(s)
        if spec.get("button"):
            out.append(button(CX, y, CW, spec["button"][0], spec["button"][1], 42))
            y += 42
        # The tab bar is drawn *after* the body and is opaque, so a screen with
        # one card too many does not look crowded — it looks finished, with the
        # overflow silently painted over. On the live-desks screen that hid
        # `Ring the bell` completely, which is the button the screen exists
        # for, and nothing said so because everything above it rendered fine.
        if y > SY + SH - 52:
            raise ValueError(
                f'screen {num} runs {y - (SY + SH - 52):.0f}px past the tab '
                f'bar — the last thing on it will be painted over')

    out += tabbar(spec.get("tabs", MAIN), spec.get("tab", 0))
    # The help button sits in the bottom trailing corner, which is exactly
    # where a live room's reaction strip ends. It stands down rather than
    # landing on the share button — a floating helper that covers a control is
    # worse than no floating helper.
    if not spec.get("live_bar"):
        out += help_button()
    out += navbar()
    # Drawn after the tab bar so nothing sits on top of it, and before close()
    # because close() emits the closing tag — appending past it produced a
    # valid-looking file that no renderer would parse.
    if spec.get("overlay_agents"):
        out += agent_overlay(spec["overlay_agents"])
    out += close()

    return "".join(out)


# --------------------------------------------------------------------------- #
# full screen — the video with the app taken off it
# --------------------------------------------------------------------------- #
def avatar_grid(x, y, w, h, people, cols=2, pad=10):
    """An audio room: everyone as a box, because there is nothing to look at.

    A voice call with no video is the case every layout forgets, and the boxes
    are not decoration — they are the only way to answer the two questions an
    audio room actually raises: *who is here* and *who is talking*. So the
    speaking ring is the loudest thing in the tile, and a muted person keeps
    their box rather than vanishing from it. Somebody who has gone quiet is
    still in the room, and a UI that removes them is telling the others they
    left.

    Synthetic profiles wear their AI badge here exactly as they do everywhere
    else. A room is a surface like any other, and a mark that switches off when
    the layout changes is a mark nobody can rely on.
    """
    o = []
    rows = (len(people) + cols - 1) // cols
    bw = (w - pad * (cols - 1)) / cols
    bh = (h - pad * (rows - 1)) / rows
    for i, (name, b64, state, badge) in enumerate(people):
        bx = x + (i % cols) * (bw + pad)
        by = y + (i // cols) * (bh + pad)
        live = state == "speaking"
        o.append(rrect(bx, by, bw, bh, 16,
                       "rgba(16,12,40,0.72)" if not live
                       else A(C["green"], 0.14),
                       A(C["green"], 0.85) if live else "rgba(255,255,255,0.08)",
                       2 if live else 1))
        r = min(bw, bh) * 0.26
        fcx, fcy = bx + bw / 2, by + bh / 2 - 6
        if live:
            # The ring, not a waveform. A waveform on a still image is a
            # picture of sound that is not happening.
            o.append(f'<circle cx="{fcx}" cy="{fcy}" r="{r+7}" fill="none" '
                     f'stroke="{A(C["green"], 0.55)}" stroke-width="2.5"/>')
        o.append(face(fcx, fcy, r * 2, b64, radius=r))
        o.append(text(fcx, by + bh - 16, name, 9.5, "#efecff", 700, "middle"))
        if badge:
            bwid = 8 + tw.width(badge, 6.4, 800)
            o.append(rrect(bx + 8, by + 8, bwid, 13, 6.5, A(C["cyan"], 0.22)))
            o.append(text(bx + 8 + bwid / 2, by + 17.5, badge, 6.4,
                          C["cyan"], 800, "middle"))
        if state == "muted":
            # A slash through a microphone, drawn rather than implied by a
            # dimmed tile: dimming means "away" on every other surface here.
            o.append(f'<circle cx="{bx+bw-16}" cy="{by+16}" r="9" '
                     f'fill="rgba(8,6,20,0.72)"/>')
            o.append(icon("mic", bx + bw - 16, by + 16, C["t3"], 0.42))
            o.append(f'<path d="M{bx+bw-22} {by+10} l12 12" stroke="{C["red"]}"'
                     f' stroke-width="1.8" stroke-linecap="round"/>')
    return o


def ar_presence(x, y, w, h, people):
    """The others, placed in the room the camera is actually looking at.

    This is the whole of what AR is over a video call: they are not in a strip
    down the side, they are *somewhere* — beside the desk, by the door — and
    where they are is information. A floor ring under each one is what makes
    them stand in the room rather than float on the glass, and it is the only
    part of this drawing doing real work.

    Marked, obviously. A synthetic profile standing in somebody's actual office
    is the single place a missing AI badge would matter most.
    """
    o = []
    for name, b64, fx, fy, scale in people:
        cx_, cy_ = x + w * fx, y + h * fy
        r = min(w, h) * 0.075 * scale
        o.append(f'<ellipse cx="{cx_}" cy="{cy_+r*1.45}" rx="{r*1.15}" '
                 f'ry="{r*0.3}" fill="{A(C["cyan"], 0.22)}"/>')
        o.append(f'<circle cx="{cx_}" cy="{cy_+r*1.45}" rx="{r*1.15}" '
                 f'r="{r*1.15}" fill="none" stroke="{A(C["cyan"], 0.35)}" '
                 f'stroke-width="1" transform="matrix(1,0,0,0.26,0,'
                 f'{cy_+r*1.45-(cy_+r*1.45)*0.26:.2f})"/>')
        o.append(f'<circle cx="{cx_}" cy="{cy_}" r="{r+4}" fill="none" '
                 f'stroke="{A(C["cyan"], 0.55)}" stroke-width="1.4"/>')
        o.append(face(cx_, cy_, r * 2, b64, radius=r))
        nw = tw.width(name, 8.4, 700) + 14
        o.append(rrect(cx_ - nw / 2, cy_ + r + 6, nw, 16, 8,
                       "rgba(8,6,20,0.70)"))
        o.append(text(cx_, cy_ + r + 17, name, 8.4, "#dff3ff", 700, "middle"))
    return o


def vastscape_scene(x, y, w, h, people):
    """The vastscape: what is being watched fills the wall, and the people
    watching rest inside it as their own faces — profile bubbles in the
    scape, not a strip of tiles down an edge.

    Drawn for the screen a console or TV casts to. On a phone the app is the
    window; here the room's biggest screen is the window and the phone is
    only the remote — so presence has to live *inside* the picture, where a
    couch full of people would actually be.
    """
    o = [rrect(x, y, w, h, 18, "#070517")]
    # The wall: a vast landscape being watched, drawn not photographed.
    wx, wy = x + w * 0.06, y + h * 0.07
    ww, wh = w * 0.88, h * 0.56
    o.append(rrect(wx, wy, ww, wh, 10, "#0d0a26", A(C["brandA"], 0.45), 1.2))
    for i, a in enumerate((0.16, 0.11, 0.07)):
        o.append(rrect(wx + 2, wy + 2 + i * wh * 0.16, ww - 4, wh * 0.16, 4,
                       A(C["indigo"], a)))
    o.append(f'<circle cx="{wx+ww*0.68:.1f}" cy="{wy+wh*0.42:.1f}" '
             f'r="{wh*0.16:.1f}" fill="{A(C["amber"], 0.85)}"/>')
    o.append(f'<path d="M{wx:.1f} {wy+wh*0.78:.1f} L{wx+ww*0.22:.1f} '
             f'{wy+wh*0.52:.1f} L{wx+ww*0.44:.1f} {wy+wh*0.80:.1f} '
             f'L{wx+ww*0.66:.1f} {wy+wh*0.60:.1f} L{wx+ww:.1f} '
             f'{wy+wh*0.84:.1f} L{wx+ww:.1f} {wy+wh:.1f} L{wx:.1f} '
             f'{wy+wh:.1f} Z" fill="{A(C["brandA"], 0.30)}"/>')
    o.append(f'<path d="M{wx:.1f} {wy+wh*0.88:.1f} L{wx+ww*0.30:.1f} '
             f'{wy+wh*0.68:.1f} L{wx+ww*0.58:.1f} {wy+wh*0.90:.1f} '
             f'L{wx+ww*0.82:.1f} {wy+wh*0.72:.1f} L{wx+ww:.1f} '
             f'{wy+wh*0.92:.1f} L{wx+ww:.1f} {wy+wh:.1f} L{wx:.1f} '
             f'{wy+wh:.1f} Z" fill="{A(C["indigo"], 0.5)}"/>')
    # The cast pill: this frame is the TV's, and says so.
    pw_ = tw.width("CAST · ON THE TV", 8.6, 700) + 16
    o.append(rrect(wx + 10, wy + 10, pw_, 20, 10, "rgba(8,6,20,0.72)"))
    o.append(text(wx + 10 + pw_ / 2, wy + 24, "CAST · ON THE TV", 8.6,
                  C["cyan"], 700, "middle"))
    # The watchers, resting in the scape below the wall — the same marked
    # bubbles AR uses, because presence is presence on every surface.
    o += ar_presence(x, y, w, h, people)
    return o


def space_scene(x, y, w, h, avatars, label="VR", uid="sp"):
    """A room that is not a place: the 3-D space people meet inside.

    Drawn rather than photographed, because there is no photograph of a
    synthetic room and using one would be a picture of somewhere that does not
    exist. A horizon, a floor receding to a vanishing point, and the people in
    it standing at different depths — which is the whole of what 3-D buys over
    a grid of boxes, and the reason a room like this is worth having at all.

    The people are the same portraits as everywhere else, with the same AI
    badge. A profile does not become anonymous by walking into a rendered room.
    """
    o = [rrect(x, y, w, h, 0, "#07051a")]
    horizon = y + h * 0.44
    o.append(f'<ellipse cx="{x+w/2}" cy="{horizon}" rx="{w*0.62}" '
             f'ry="{h*0.20}" fill="url(#glow)" opacity="0.55"/>')
    # Floor: lines to a vanishing point, and rungs spaced so they crowd toward
    # it. Even spacing reads as a flat grid seen from above, which is the one
    # thing this drawing must not look like.
    vpx, vpy = x + w / 2, horizon
    for i in range(-7, 8):
        o.append(f'<path d="M{vpx} {vpy} L{x+w/2+i*(w/5)} {y+h}" '
                 f'stroke="rgba(150,130,255,0.20)" stroke-width="1" '
                 f'fill="none"/>')
    for k in range(1, 9):
        t = k / 9
        yy = horizon + (y + h - horizon) * (t ** 2.1)
        o.append(f'<path d="M{x} {yy} H{x+w}" '
                 f'stroke="rgba(150,130,255,{0.06+0.16*t:.2f})" '
                 f'stroke-width="1"/>')
    # Standing presences, near ones larger and lower. Depth is carried by size
    # and position rather than by a shadow, which at this scale is a smudge.
    for name, b64, depth in avatars:
        scale = 0.55 + 0.45 * depth
        r = min(w, h) * 0.085 * (0.8 + 0.6 * depth)
        cx_ = x + w * (0.5 + (depth - 0.5) * 0.9) if len(avatars) > 1 else x + w / 2
        cy_ = horizon + (y + h - horizon) * (0.10 + 0.40 * depth)
        o.append(f'<ellipse cx="{cx_}" cy="{cy_+r*1.5}" rx="{r*1.1}" '
                 f'ry="{r*0.28}" fill="rgba(150,130,255,{0.10+0.14*depth:.2f})"/>')
        o.append(f'<circle cx="{cx_}" cy="{cy_}" r="{r+5}" fill="none" '
                 f'stroke="{A(C["brandA"], 0.45)}" stroke-width="1.4"/>')
        o.append(face(cx_, cy_, r * 2, b64, radius=r))
        o.append(text(cx_, cy_ + r + 16, name, 8.6 * (0.85 + 0.3 * scale),
                      "#e6e1ff", 650, "middle"))
    if label:
        lw = 16 + tw.width(label, 9, 800)
        o.append(rrect(x + w - lw - 22, y + 20, lw, 20, 10,
                       A(C["brandA"], 0.30)))
        o.append(text(x + w - lw / 2 - 22, y + 34, label, 9, "#fff", 800,
                      "middle"))
    return o


def video_facade(x, y, w, h, platform, title, note, uid="vf", cyf=0.5,
                 bottom_note=True):
    """A video from another platform, before anybody presses play.

    There is deliberately no thumbnail here, and the empty plate is the point
    rather than a gap in the mock. A normal embed loads the other company's
    player the moment the page renders, which tells them you looked before you
    decided to; QRME renders the platform's name, the poster's own words and a
    play control, all served from this side. Pressing play is when the request
    happens — see ``qrme/embeds.py``.

    Drawing a YouTube thumbnail here would have been the prettier mock and a
    picture of the thing the code refuses to do.
    """
    o = [rrect(x, y, w, h, 14, "#0d0a1c", A(C["line"], 0.9), 1)]
    cy = y + h * cyf - 8
    o.append(f'<circle cx="{x+w/2}" cy="{cy}" r="26" '
             f'fill="rgba(255,255,255,0.10)" '
             f'stroke="rgba(255,255,255,0.35)" stroke-width="1.2"/>')
    o.append(f'<path d="M{x+w/2-7} {cy-10} L{x+w/2+11} {cy} '
             f'L{x+w/2-7} {cy+10} Z" fill="rgba(255,255,255,0.92)"/>')
    # The platform chip, top-left, where a source belongs.
    pw = 16 + tw.width(platform, 9, 750)
    o.append(rrect(x + 10, y + 10, pw, 20, 10, "rgba(255,255,255,0.12)"))
    o.append(text(x + 10 + pw / 2, y + 24, platform, 9, "#fff", 750, "middle"))
    if title:
        o.append(text(x + w / 2, cy + 48, title, 11, "#efecff", 650, "middle"))
    if note and bottom_note:
        o.append(rrect(x, y + h - 30, w, 30, 0, "rgba(6,4,16,0.72)"))
        o.append(icon("lock", x + 18, y + h - 15, C["green"], 0.46))
        o.append(text(x + 30, y + h - 11, note, 8.2, "#cfe8d6", 600))
    elif note:
        # Full screen has a strip along the bottom already, so the promise sits
        # under the title instead of in a bar that would land on the composer.
        o.append(icon("lock", x + w / 2 - tw.width(note, 8.6, 600) / 2 - 8,
                      cy + 66, C["green"], 0.46))
        o.append(text(x + w / 2 + 6, cy + 69, note, 8.6, "#cfe8d6", 600,
                      "middle"))
    return "".join(o)


def held_controls(sx, sy, sw, sh, kinds, landscape=False, cyf=0.5):
    """What a long press puts back on the picture.

    The help button used to be on every screen unconditionally, on the theory
    that "on all screens" is a property of the chrome rather than something 88
    screens can each be trusted to remember. That theory is right everywhere
    except here, where the chrome *is* the thing being taken away: a floating
    helper welded to the corner of a full-screen video is a permanent smudge on
    it, and it sits exactly where the share button now goes.

    So on a live surface it comes back the way everything else does — you press
    and hold, and the controls surface. That keeps the promise (help is never
    more than a gesture away) without keeping the pixel.

    The scrim is the honest part of the drawing. Long-press states are usually
    illustrated as a picture with buttons floating on it, which is not what a
    phone does — it dims what you are holding, so the controls read and so it
    is obvious the picture is still there underneath, waiting.
    """
    # Dimmed hard, not tinted. The point of the state is that there is exactly
    # one bright thing on the glass and it is the thing you can press; a light
    # scrim leaves the picture competing with the buttons and turns a decision
    # into a hunt. Tapping anywhere else takes the dim away again, which is why
    # nothing else needs to be lit.
    o = [rrect(sx, sy, sw, sh, 40, "rgba(4,3,12,0.78)")]
    r = 19
    # The slot is set by the widest *caption*, not the button. Spacing them on
    # the circles put "Landscape" and "Back to app" into each other, which is
    # the same overlap that has now been shipped three times in this file.
    slot = max(r * 2, max(tw.width(k[3], 8.4, 650) for k in kinds)) + 14
    total = slot * len(kinds)
    if total > sw - 24:
        raise ValueError(f"held controls need {total:.0f}px, screen has {sw-24:.0f}")
    bx = sx + sw / 2 - total / 2 + slot / 2
    cy = sy + sh * cyf - 8
    for glyph, ic, key, label in kinds:
        col = ACCENT.get(key) or C[key]
        # Lit rather than outlined: a halo, a filled disc and a white glyph.
        # Against a 78% scrim an outlined button is a dark circle with a thin
        # edge, which is the one thing on the screen that should not read as
        # switched off.
        o.append(f'<circle cx="{bx}" cy="{cy}" r="{r+13}" '
                 f'fill="{A(col, 0.16)}"/>')
        o.append(f'<circle cx="{bx}" cy="{cy}" r="{r}" fill="{A(col, 0.92)}"/>')
        if glyph:
            o.append(text(bx, cy + 6, glyph, 19, "#0b0820", 800, "middle"))
        else:
            o.append(icon(ic, bx, cy, "#0b0820", 0.78))
        o.append(text(bx, cy + r + 17, label, 8.6, "#fff", 700, "middle"))
        bx += slot
    o.append(text(sx + sw / 2, cy - r - 20, "PRESS AND HOLD", 8.6,
                  "rgba(255,255,255,0.62)", 750, "middle", 1.4))
    o.append(text(sx + sw / 2, cy + r + 44, "tap anywhere else to go back",
                  8.2, "rgba(255,255,255,0.42)", 500, "middle"))
    return o


def render_full(spec):
    """A live room with the application taken off it.

    Portrait fills the phone's whole face — no title, no tab bar, no help
    button — because "full screen" that stops short of the chrome is just a
    larger box. Landscape is the same idea turned ninety degrees, which is what
    a phone does when you tilt it and the only shape in which a room shot
    sixteen-by-nine arrives at its own aspect ratio instead of being cropped to
    fit a column.
    """
    # The picture runs to the edge of the *file*, not to the edge of a device
    # drawn inside a margin. Two separate borders were showing up around a
    # screen that claims to be full: the ~10px of phone body every other screen
    # draws around its display, and the transparent margin this canvas leaves
    # around the phone — which is invisible on a dark page and a white band on
    # a light one. Both are gone. A screenshot of a full screen is the screen.
    w, h = (H, W) if spec.get("landscape") else (W, H)
    land = spec.get("landscape", False)
    sx, sy, sw, sh = 0, 0, w, h
    sradius = 28

    ac = ACCENT.get(spec.get("accent", "brand"), C["brandA"])
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}" role="img" '
           f'aria-label="{esc(spec["title"])} screen">', defs(ac)]
    out.append(rrect(sx, sy, sw, sh, sradius, "url(#gScr)"))

    if spec.get("voices"):
        # An audio room has no picture, so the boxes *are* the screen. Inset
        # from the edges the way a photo is not: a grid pushed into the corner
        # radius loses its corner tiles.
        out.append(rrect(sx, sy, sw, sh, sradius, "#0a0820"))
        used_bar = D_BTN + 18
        out += avatar_grid(sx + 16, sy + 46, sw - 32,
                           sh - 46 - used_bar - 18, spec["voices"],
                           cols=3 if land else 2)
    elif spec.get("space"):
        out += space_scene(sx, sy, sw, sh, spec["space"]["avatars"],
                           label=spec["space"].get("label", "VR"),
                           uid=f's{spec["num"]}')
    elif spec.get("vastscape"):
        out += vastscape_scene(sx, sy, sw, sh, spec["vastscape"]["avatars"])
    elif spec.get("facade"):
        # Full screen on a video nobody has pressed play on yet is an empty
        # screen, and drawing a still from the video would be a picture of the
        # request this design refuses to make.
        f = spec["facade"]
        out.append(rrect(sx, sy, sw, sh, sradius, "#08061a"))
        out.append(video_facade(sx, sy, sw, sh, f["platform"], f["title"],
                                f["note"], uid=f'f{spec["num"]}',
                                cyf=0.38 if spec.get("held") else 0.46,
                                bottom_note=False))
    else:
        cid = f'clipfull{spec["num"]}'
        out.append(f'<clipPath id="{cid}"><rect x="{sx}" y="{sy}" '
                   f'width="{sw}" height="{sh}" rx="{sradius}"/></clipPath>')
        out.append(f'<image x="{sx}" y="{sy}" width="{sw}" height="{sh}" '
                   f'preserveAspectRatio="xMidYMid slice" '
                   f'clip-path="url(#{cid})" '
                   f'href="data:image/jpeg;base64,{spec["photo"]}"/>')

    # The camera cut-out is a property of the hardware, so it rotates with the
    # phone and it keeps its platform's shape — an iOS pill on an Android
    # frame was the tell that this renderer was ignoring PLATFORM entirely.
    hole = "#05070d"
    if PLATFORM == "android":
        cxh, cyh = (sx + 13, h / 2) if land else (w / 2, sy + 13)
        out.append(f'<circle cx="{cxh}" cy="{cyh}" r="4.5" fill="{hole}"/>')
    elif land:
        out.append(rrect(sx + 5, h / 2 - 30, 15, 60, 7.5, hole))
    else:
        out.append(rrect(w / 2 - 30, sy + 5, 60, 15, 7.5, hole))

    tx = sx + (34 if land else 20)
    if spec.get("photo_tag"):
        label, tone = spec["photo_tag"]
        col = {"live": C["red"], "sample": C["t2"], "rated": C["red"]}[tone]
        tagw = 16 + len(label) * 6.2
        out.append(rrect(tx, sy + 20, tagw, 20, 10, "rgba(8,6,20,0.72)"))
        out.append(f'<circle cx="{tx+11}" cy="{sy+30}" r="3.4" fill="{col}"/>')
        out.append(text(tx + 19, sy + 34, label, 9, "#fff", 750, "start", 0.4))
        tx += tagw + 6
    # A rated stream keeps its badge in full screen. The gate is a property of
    # the profile, not of the chrome, so taking the chrome away must not take
    # it with them.
    if spec.get("rated"):
        out.append(rrect(tx, sy + 20, 38, 20, 10, A(C["red"], 0.85)))
        out.append(text(tx + 19, sy + 34, "18+", 9.5, "#fff", 800, "middle"))
        tx += 44

    # Whose live this is, and it is not decoration.
    #
    # The `NOT AI · REAL PERSON` mark says a human is behind the camera. It
    # deliberately says nothing about the mask over their face, and the reason
    # it can afford not to is that the viewer already knows *whose* stream they
    # are on. That was asserted before it was drawn — the top-left carried the
    # LIVE pill and nothing else — so the argument was resting on chrome that
    # did not exist.
    #
    # Top left, beside the LIVE pill, on every surface with a picture: a live
    # desk, a room, a rated stream, a watch party, full screen and landscape
    # alike. Full screen is where it matters most, because that is the state
    # with the app's own header taken away.
    if spec.get("whose"):
        handle = spec["whose"]
        hw = 26 + len(handle) * 6.0
        out.append(rrect(tx, sy + 20, hw, 20, 10, "rgba(8,6,20,0.72)"))
        out.append(f'<circle cx="{tx+11}" cy="{sy+30}" r="6" '
                   f'fill="{A(C["brandA"], 0.9)}"/>')
        out.append(f'<circle cx="{tx+11}" cy="{sy+28.2}" r="2.1" fill="#fff"/>')
        out.append(f'<path d="M{tx+7.4} {sy+33.6} c0 -3.4 {7.2} -3.4 {7.2} 0" '
                   f'fill="none" stroke="#fff" stroke-width="1.5" '
                   f'stroke-linecap="round"/>')
        out.append(text(tx + 21, sy + 34, handle, 9.5, "#fff", 700, "start"))
        tx += hw + 6

    if spec.get("ar_presence"):
        out += ar_presence(sx, sy, sw, sh, spec["ar_presence"])

    bar, used = live_bar(sx, sy, sw, sh, spec["live_bar"])
    rows = spec.get("bubble_chat", [])
    if rows:
        cw = (sw * 0.62) if land else (sw - 28)
        block, _ = bubble_chat(sx + (32 if land else 14),
                               sy + sh - 12 - used - len(rows) * 30, cw, rows)
        out += block
    out += bar

    if spec.get("held"):
        out += held_controls(sx, sy, sw, sh, spec["held"], landscape=land,
                             cyf=0.68 if spec.get("facade") else 0.5)

    # The system navigation, on the edge the hand is holding. Android's three
    # marks turn with the phone the way iOS's single bar does; drawing the iOS
    # bar on both was the other half of the same PLATFORM bug.
    stroke = 'fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.3"'
    if PLATFORM == "android":
        if land:
            ax, ay = sx + sw - 12, h / 2
            out.append(f'<path d="M{ax-4.5} {ay-34+5} L{ax} {ay-34-5} '
                       f'L{ax+4.5} {ay-34+5} Z" {stroke} stroke-linejoin="round"/>')
            out.append(f'<circle cx="{ax}" cy="{ay}" r="4.6" {stroke}/>')
            out.append(rrect(ax - 4.6, ay + 34 - 4.6, 9.2, 9.2, 1.6, "none",
                             "rgba(255,255,255,0.5)", 1.3))
        else:
            ax, ay = w / 2, sy + sh - 14
            out.append(f'<path d="M{ax-34+5} {ay-4.5} L{ax-34-5} {ay} '
                       f'L{ax-34+5} {ay+4.5} Z" {stroke} stroke-linejoin="round"/>')
            out.append(f'<circle cx="{ax}" cy="{ay}" r="4.6" {stroke}/>')
            out.append(rrect(ax + 34 - 4.6, ay - 4.6, 9.2, 9.2, 1.6, "none",
                             "rgba(255,255,255,0.5)", 1.3))
    elif land:
        out.append(rrect(sx + sw - 8, h / 2 - 40, 4, 80, 2,
                         "rgba(255,255,255,0.55)"))
    else:
        out.append(rrect(w / 2 - 55, sy + sh - 10, 110, 4, 2,
                         "rgba(255,255,255,0.55)"))
    out += close()
    return "".join(out)


# --------------------------------------------------------------------------- #
# screen definitions — a screen for every capability
# --------------------------------------------------------------------------- #
SCREENS = [
    # ---- core onboarding & identity (the mockup) ----
    dict(num=1, title="Welcome", sub="Onboarding & consent", hero="welcome", accent="brand", tab=0),
    dict(num=2, title="Create Profile", sub="Choose who this AI is", hero="types", accent="brand", tab=0),
    dict(num=3, title="Build Your Profile", sub="Add memories & knowledge", hero="sources", accent="cyan", tab=0),
    dict(num=4, title="Personality", sub="Shape how your AI interacts", hero="personality", accent="brand", tab=0),
    dict(num=5, title="Profile Home", sub="Your AI, at a glance", hero="profilehome", accent="brand", tab=0),
    dict(num=6, title="Chat", sub="Every response explained", hero="chat", accent="brand", tab=0),
    dict(num=7, title="Memory Vault", sub="Your AI remembers", hero="vault", accent="cyan", tabs=VAULT, tab=0, locked=True),
    dict(num=8, title="Relationships", sub="People it knows", hero="relationships", accent="amber", tabs=REL, tab=0),
    dict(num=9, title="Add Relationship", sub="Relationship-aware behavior", hero="addrel", accent="amber", tabs=REL, tab=0),
    dict(num=10, title="Profile Health", sub="At a glance", hero="health", accent="green", tab=2),
    dict(num=11, title="Marketplace", sub="Discover & connect", hero="marketplace", accent="amber", tabs=MARKET, tab=0),
    dict(num=12, title="Licensing Center", sub="License your expertise", hero="licensing", accent="amber", tabs=LICENSE, tab=0),
    dict(num=13, title="Embodiments", sub="Your AI everywhere", hero="embodiments", accent="cyan", tab=3),
    dict(num=14, title="Control Center", sub="You are in control", hero="control", accent="green", tabs=CONTROL, tab=0),
    dict(num=15, title="Design Language", sub="One world, one system", hero="design", accent="brand", tab=3),
    # ---- companion & summoning ----
    dict(num=16, title="Genesis", sub="Born from four questions", hero="genesis", accent="brand", tab=0),
    dict(num=17, title="Summon & Beacons", sub="Leave your AI in the world", hero="beacon", accent="brand", tab=0),
    dict(num=18, title="Proactive", sub="It reaches out first", accent="pink", tab=0, cards=[
        dict(icon="chat", color="pink", k="“The garden?”", s="only if you set proactive scope", pill=("SCOPED", "brand")),
        dict(icon="clock", color="cyan", k="Quiet hours honored", s="22:00 – 07:00 · rate-capped 24h"),
        dict(icon="shieldok", color="green", k="Moderated & anti-spam", s="no repeat until you reply"),
    ], button=("Reply", "brand")),
    dict(num=19, title="Transparency", sub="Honest about multiplicity", accent="brand", tab=0, cards=[
        dict(icon="people", color="brand", k="12 relationships", s="acknowledged truthfully if asked", pill=("OPEN", "brand")),
        dict(icon="eye", color="cyan", k="GET /transparency", s="who it talks to, by design"),
        dict(icon="chat", color="amber", k="“Yes, I know others too.”", s="every prompt instructs honesty"),
    ]),
    dict(num=20, title="Connections", sub="Meet other real people", accent="pink", tab=0, tabs=MARKET, cards=[
        dict(icon="people", color="pink", k="Friendly tier", s="matched anonymously by alias", pill=("OPEN", "good")),
        dict(icon="shield", color="red", k="Rated tier · 18+", s="age-verified both ends"),
        dict(icon="warn", color="amber", k="Per-tier moderation", s="minors strict · blocks never sent"),
    ]),
    dict(num=21, title="Rooms", sub="Chat, voice, video, AR, VR", accent="cyan", tab=0, cards=[
        dict(icon="chat", color="brand", k="Multiparty conversation", s="users + profiles, any mix"),
        dict(icon="people", color="cyan", k="profile ↔ profile", s="they advance on their own"),
        dict(icon="headset", color="pink", k="Any channel", s="chat · voice · video · AR · VR"),
        dict(icon="shieldok", color="green", k="A minor present → strict", s="every profile turn moderated"),
    ]),
    dict(num=22, title="Providers", sub="When AI hands off to a human", accent="cyan", tab=0, tabs=MARKET, cards=[
        dict(icon="cross", color="red", k="Bay Area Wellness", s="mental health · 0.8 mi", pill=("OPEN", "good")),
        dict(icon="chart", color="green", k="Certified Planner", s="finance · telehealth"),
        dict(icon="link", color="cyan", k="Consented handoff", s="sealed in the vault, revocable"),
    ]),
    # ---- data promise & lifecycle ----
    dict(num=23, title="Cloud Model", sub="Greater model, opt-in", hero="cloud", accent="brand", tabs=CONTROL, tab=0),
    dict(num=24, title="Offline Mode", sub="A hard guarantee", hero="offline", accent="green", tabs=CONTROL, tab=0),
    dict(num=25, title="Objection & Lifecycle", sub="A real person can contest", hero="objection", accent="amber", tab=0),
    dict(num=26, title="Memorial", sub="Graceful departure", hero="memorial", accent="cyan", tab=0),
    # ---- assistant & claims 21–26 ----
    dict(num=27, title="AI Assistant", sub="A capable creative partner", accent="brand", tab=0, cards=[
        dict(icon="list", color="brand", k="Triage & curate", s="keep the best N, auditable score"),
        dict(icon="pen", color="amber", k="Proofread in your voice", s="improved draft + suggestions"),
        dict(icon="eye", color="cyan", k="Perceive the scene", s="hands-free, step by step"),
        dict(icon="star2", color="pink", k="Compose a work", s="music, poem, note — kept"),
    ]),
    dict(num=28, title="Specialists", sub="Biometric-routed handoff", accent="cyan", tab=0, cards=[
        dict(icon="heart", color="red", k="Stress detected", s="HR +38 · from JIM-mini", extra=("spark", [60, 68, 80, 95, 108], "red")),
        dict(icon="brain", color="pink", k="Handed off", s="mental-health agent, this turn", pill=("ENGAGED", "brand")),
        dict(icon="link", color="cyan", k="Sustained across turns", s="until a reading shows recovery"),
        dict(icon="person", color="green", k="Hands back", s="profile speaks again", pill=("RETURNED", "good")),
    ]),
    dict(num=29, title="Tasks & Grants", sub="Autonomous, revocable", accent="amber",
         tab=0, light=("amber", "needs you — awaiting confirm"), cards=[
        dict(icon="gift", color="amber", k="Grant issued", s="a revocable vault token", pill=("SCOPED", "brand")),
        dict(icon="list", color="brand", k="research → draft → send", s="one phase at a time"),
        dict(icon="clock", color="cyan", k="Pauses at confirm", s="resumes in a later session"),
        dict(icon="warn", color="red", k="Revoke halts the read", s="raw data never retained"),
    ]),
    dict(num=30, title="Fine-Tune", sub="Encrypted, offline (Claim 26)", accent="green", tab=2, cards=[
        dict(icon="sliders", color="green", k="Recompute", s="all local · no external calls", pill=("LOCAL", "good")),
        dict(icon="lock", color="cyan", k="Sealed in the vault", s="adaptation artifact encrypted"),
        dict(icon="chart", color="brand", k="Run recorded", s="external_transmission: false"),
    ], button=("Run Fine-Tune", "brand")),
    dict(num=31, title="Your Data Promise", sub="No raw data leaves your vault", accent="green", tabs=CONTROL, tab=0, cards=[
        dict(icon="lock", color="green", k="Sealed at rest", s="AES-256-GCM · tenant-isolated", pill=("VAULT", "good")),
        dict(icon="eye", color="cyan", k="Access audited", s="stored · read · erased", pill=("CHAIN OK", "good")),
        dict(icon="finger", color="brand", k="Capability tokens", s="only the SHA-256 hash is stored"),
        dict(icon="warn", color="red", k="Delete anything, anytime", s="local trace + vault records"),
    ]),
    # ---- moderation, posting & the persona engine ----
    dict(num=32, title="Moderation", sub="Every reply, before it's seen", hero="moderation", accent="green", tab=0),
    dict(num=33, title="Posts", sub="Post in your AI's voice", accent="amber", tabs=MARKET, tab=3, cards=[
        dict(icon="pen", color="amber", k="Compose a post", s="in its own voice, moderated"),
        dict(icon="chat", color="brand", k="“Tomatoes at last.”", s="posted to the feed", pill=("LIVE", "good")),
        dict(icon="shieldok", color="green", k="Public posts → strict", s="always the strict filter"),
        dict(icon="chart", color="cyan", k="12 posts · 3.4k views", s="GET /posts"),
    ]),
    dict(num=34, title="Adult Mode", sub="Age-gated at both ends", accent="red", tab=0, locked=True, cards=[
        dict(icon="lock", color="red", k="Adult content mode", s="an adult owner must enable it", pill=("18+", "crit")),
        dict(icon="finger", color="green", k="Owner is 18+", s="required to turn it on", stat=("VERIFIED", "on")),
        dict(icon="person", color="amber", k="Interactor 18+", s="verified before chat", stat=("REQUIRED", "avail")),
        dict(icon="shieldok", color="cyan", k="Minors always strict", s="no exceptions, ever"),
    ]),
    dict(num=35, title="Aging & Lifecycle", sub="It evolves with time", accent="cyan", tab=0, cards=[
        dict(icon="clock", color="cyan", k="Effective age", s="base 41 · +2y elapsed", metric="43"),
        dict(icon="leaf", color="green", k="Aging enabled", s="grows with real time", stat=("ON", "on")),
        dict(icon="people", color="amber", k="Successor owner", s="legacy succession set", stat=("SET", "on")),
        dict(icon="dove", color="pink", k="Or sunsets to memorial", s="never orphaned"),
    ]),
    dict(num=36, title="Multi-Modal", sub="Text, voice, image, video", hero="modal", accent="brand", tab=0),
    dict(num=37, title="Persona Embedding", sub="Latent state · Claims 21–23", hero="embedding", accent="brand", tab=2),
    dict(num=38, title="Surfaces", sub="Cross-platform presence", accent="cyan", tab=3, cards=[
        dict(icon="chat", color="brand", k="Chat", s="in-app conversation", stat=("ON", "on")),
        dict(icon="grid", color="amber", k="Feed", s="posts & stories", stat=("ON", "on")),
        dict(icon="compass", color="green", k="Web", s="public profile page", stat=("ON", "on")),
        dict(icon="headset", color="pink", k="AR / VR", s="immersive rooms", stat=("OFF", "off")),
        dict(icon="watch", color="cyan", k="Wearable", s="ambient presence", stat=("ON", "on")),
    ]),
    # ---- session lifecycle (sign-in → … → sign-out) ----
    dict(num=39, title="Sign In", sub="Welcome back", hero="signin", accent="brand", tab=0),
    dict(num=40, title="End Session", sub="Your vault is sealed", hero="endsession", accent="green", tab=0),
    # ---- first-run: account, verification & guided setup ----
    dict(num=41, title="Log In", sub="Apple, Google or email", hero="auth", accent="brand", tab=0),
    dict(num=42, title="Verify Identity", sub="Real person, once", hero="verify", accent="brand", tab=0),
    dict(num=43, title="Enable Access", sub="Permissions, your call", hero="permissions", accent="cyan", tab=0),
    dict(num=44, title="Avatar Studio", sub="A 2D & 3D face for Ava", hero="avatar", accent="brand", tab=0),
    # ---- immersive surfaces: avatar chat, AR/VR & live video ----
    dict(num=45, title="Immersive Chat", sub="AR / VR, life-size avatar", hero="immersive", accent="cyan", tab=0),
    dict(num=46, title="Live Video", sub="Face-to-face with your AI", hero="video", accent="brand", tab=0),
    dict(num=47, title="All Set", sub="Onboarding complete", hero="allset", accent="green", tab=0),
    dict(num=48, title="Social Connections", sub="Collect data · publish & run", hero="social", accent="brand", tab=0),
    dict(num=49, title="Connected Apps", sub="Apple · Google · Microsoft · Canva", hero="connectedapps", accent="brand", tab=0),
    dict(num=50, title="Knowledge Excursions", sub="Study safely · private data stays home", hero="excursions", accent="brand", tab=0),
    dict(num=51, title="Files & Photos", sub="Connect your device files & photos", hero="filesphotos", accent="brand", tab=0),
    dict(num=52, title="Apple Intelligence", sub="13 apps · collect, act, produce", hero="assistant", provider="apple", accent="brand", tab=0),
    dict(num=53, title="Google Gemini", sub="11 apps · collect, act, produce", hero="assistant", provider="google", accent="brand", tab=0),
    dict(num=54, title="Microsoft Copilot", sub="8 apps · collect, act, produce", hero="assistant", provider="microsoft", accent="brand", tab=0),
    dict(num=55, title="Objection & Revocation", sub="Contested profile · vault-sealed audit", hero="objectionaudit", accent="brand", tab=3),
    dict(num=56, title="Robotics", sub="Same persona · a physical body", hero=None, accent="brand", tab=0, cards=[
        dict(icon="person", color="brand", k="NEO · 1X", s="Humanoid · Grok onboard · active"),
        dict(icon="star2", color="cyan", k="Isaac 1 · Weave", s="Home robot · tidying · docked"),
        dict(icon="grid", color="green", k="Saros 20 · Roborock", s="Vacuum · mapping · patrol 9pm"),
        dict(icon="shield", color="amber", k="Command allowlist", s="per-body limits · moderated"),
        dict(icon="list", color="pink", k="Command log", s="Every order audited"),
    ], button=("Bind a robot", "brand")),
    # ---- knowledge packs & robot task mods ----
    dict(num=57, title="Knowledge Packs", sub="Downloadable expertise, per industry", accent="amber", tabs=MARKET, tab=0, cards=[
        dict(icon="db", color="amber", k="Finance Field Pack", s="3 items · QRME Starter Collection", pill=("FREE", "good")),
        dict(icon="db", color="brand", k="Systems Pro pack", s="priced · explicit accept to buy", pill=("$29.99", "warn")),
        dict(icon="star2", color="green", k="Install → smarter", s="items join the source material"),
        dict(icon="eye", color="cyan", k="Provenance counts it", s="grounded_in.by_kind: pack"),
    ], button=("Download Field Pack", "brand")),
    dict(num=58, title="Robot Task Packs", sub="Task mods for the body it embodies", accent="cyan", tab=3, cards=[
        dict(icon="gear", color="cyan", k="Household Tasks", s="sort_laundry · water_plants", pill=("FREE", "good")),
        dict(icon="shield", color="green", k="Checked on install", s="a vacuum is never sold guile"),
        dict(icon="lock", color="amber", k="Extended, not opened", s="unknown verbs still refused"),
        dict(icon="chart", color="pink", k="Every task audited", s="procedure carried in the result"),
    ], button=("Buy Culinary Assistant · 9.99", "brand")),
    dict(num=59, title="Embodied Agent", sub="The persona knows its body", accent="brand", tab=3, cards=[
        dict(icon="person", color="brand", k="Same identity, in a body", s="never a second persona"),
        dict(icon="star2", color="cyan", k="Learned, in the prompt", s="say knows what the body can do"),
        dict(icon="grid", color="green", k="Skills list", s="GET /robots/{id}/skills"),
        dict(icon="shieldok", color="amber", k="Revocable", s="uninstall revokes the verbs"),
    ]),
    dict(num=60, title="Publish a Pack", sub="Your expertise, on the market", accent="amber", tabs=MARKET, tab=0, cards=[
        dict(icon="pen", color="amber", k="Bundle knowledge items", s="or task modules, with needs"),
        dict(icon="chart", color="brand", k="Free or priced", s="POST /packs · listed under #pack"),
        dict(icon="people", color="green", k="Installs tracked", s="catalog shows items · installs"),
    ], button=("Publish", "brand")),
    dict(num=61, title="Pack Registries", sub="Federated mod storefronts", accent="brand", tabs=MARKET, tab=0, cards=[
        dict(icon="building", color="brand", k="Robotmods.net", s="task mods for robot bodies", pill=("2 PACKS", "info")),
        dict(icon="building", color="cyan", k="LLMmods.com", s="knowledge mods for personas", pill=("2 PACKS", "info")),
        dict(icon="shieldok", color="green", k="Origin on every label", s="publisher & storefront on pack"),
        dict(icon="chart", color="amber", k="Same rules once synced", s="buy flow · checks · provenance"),
    ], button=("Sync sources", "brand")),
    dict(num=62, title="Rated Placement", sub="18+ marketing, walled at the source", accent="red", tabs=MARKET, tab=0, locked=True, cards=[
        dict(icon="building", color="red", k="Adult venues", s="OnlyFans · Fansly · x-rated sites", pill=("18+", "crit")),
        dict(icon="grid", color="amber", k="QR · @handle · #tag", s="publish the refs where adults are"),
        dict(icon="lock", color="green", k="The wall travels", s="every scan hits the age gate"),
        dict(icon="shieldok", color="cyan", k="Never a real person", s="self or fictional personas only"),
    ], button=("Place at a venue", "brand")),
    dict(num=63, title="Placement Analytics", sub="What each venue earns", accent="amber", tabs=MARKET, tab=0, locked=True, cards=[
        dict(icon="chart", color="amber", k="OnlyFans · 3 scans", s="2 walled · 1 verified", extra=("spark", [1, 1, 3, 2, 4], "amber")),
        dict(icon="chart", color="cyan", k="Fansly · 2 scans", s="0 walled · 2 verified"),
        dict(icon="people", color="green", k="Funnel", s="resolved → verified", metric="25%"),
        dict(icon="shieldok", color="brand", k="Counted, never identified", s="owner-only · no viewer identities"),
    ]),
    dict(num=64, title="Creator Payouts", sub="One statement, every sale", accent="green", tabs=MARKET, tab=0, cards=[
        dict(icon="chart", color="green", k="Accrued balance", s="pack sales · license fees", metric="$86"),
        dict(icon="db", color="amber", k="Systems Pro", s="pack_sale · $29.99", pill=("ACCRUED", "warn")),
        dict(icon="pen", color="brand", k="consult · Priya", s="license_fee · $49.00", pill=("PAID", "good")),
        dict(icon="shieldok", color="cyan", k="Written at sale time", s="a record, not a reconstruction"),
    ], button=("Request payout", "brand")),
    dict(num=65, title="Watch Remote", sub="Your agents, on your wrist", accent="green", tab=3, cards=[
        dict(icon="clock", color="green", k="ship the notes", s="phase: draft", pill=("WORKING", "good")),
        dict(icon="clock", color="amber", k="research brief", s="awaiting: external confirmation", pill=("NEEDS YOU", "warn")),
        dict(icon="clock", color="red", k="second job", s="cancelled from the wrist", pill=("STOPPED", "crit")),
        dict(icon="person", color="brand", k="Kitchen NEO", s="come here · patrol · dock · stop"),
        dict(icon="shieldok", color="cyan", k="Reach, not new powers", s="same auth · allowlists · rules"),
    ], button=("Assist", "brand")),
    dict(num=67, title="Smart Glasses", sub="Capture the POV, render to the lens", accent="cyan", tab=3, cards=[
        dict(icon="eye", color="cyan", k="Ray-Ban Meta", s="capture · livestream · HUD", pill=("LINKED", "good")),
        dict(icon="eye", color="brand", k="Meta Ray-Ban Display", s="POV context · HUD overlay · nav"),
        dict(icon="compass", color="green", k="Google (Android XR)", s="Gemini POV · live-translation HUD"),
        dict(icon="photo", color="amber", k="Capture ⟷ render", s="collect in · produce to the lens"),
    ], button=("Connect glasses", "brand")),
    dict(num=68, title="Gaming Companion", sub="A teammate, synthetically operated", accent="indigo", tab=3, cards=[
        dict(icon="star2", color="indigo", k="Halo Infinite · Xbox", s="role: teammate · multiplayer", pill=("LIVE", "good")),
        dict(icon="chat", color="brand", k="“Falling back, cover me”", s="in-character callout, moderated"),
        dict(icon="shieldok", color="green", k="Fair play, enforced", s="within the rules · never cheats"),
        dict(icon="people", color="cyan", k="Companion or teammate", s="PlayStation · Xbox · Switch · PC"),
    ], button=("Start a session", "brand")),
    dict(num=66, title="Steering", sub="Tone, pace, age & appearance — one hub", accent="brand", tab=2, cards=[
        dict(icon="sliders", color="brand", k="Pace · Autonomy · Words", s="throttle dials, 0–100"),
        dict(icon="sliders", color="amber", k="Warmth · Humor · Form", s="behavior dials, 0–100"),
        dict(icon="person", color="cyan", k="Appearance", s="how it looks — on every surface"),
        dict(icon="clock", color="green", k="Age", s="base age · ages with time"),
        dict(icon="lock", color="red", k="Intimacy · 18+ only", s="adult-mode profiles · in bounds", pill=("18+", "crit")),
        dict(icon="shieldok", color="green", k="Steering, not piloting", s="shapes manner, never safety"),
    ], button=("Apply", "brand")),

    # ---- live desks, the audience layer, and commerce (0.1.6 / 0.1.7) ----
    # The desk screens are the only ones in this set that must NOT show the AI
    # mark: a desk is an actual person, and stamping "AI" on them would be a
    # false statement. The badge is the positive claim instead.
    # Five cards and a button did not fit: the button — which is the whole
    # point of the screen — was drawn *below* the tab bar, where nothing
    # renders it and nobody could see it. The two attestation cards say one
    # thing between them and are now one card, and the sample view is smaller,
    # because on this screen the photo is a thumbnail of a desk nobody has
    # claimed yet rather than the subject.
    dict(num=69, title="Live Desks", sub="A real person — never the AI mark",
         accent="green", tab=3,
         photo=frames.DESK, photo_tag=("SAMPLE VIEW", "sample"), photo_h=110,
         photo_note="No camera yet — not claimed live",
         cards=[
        dict(icon="person", color="green", k="Bev Okafor",
             s="Live person — not AI", pill=("HUMAN", "good")),
        dict(icon="eye", color="cyan", k="You see the desk",
             s="a camera view, depicting nobody"),
        dict(icon="shieldok", color="brand", k="Attested, not proven",
             s="a manager vouched, not verified"),
        dict(icon="clock", color="amber", k="Away right now",
             s="the state the bell exists for", pill=("AWAY", "warn")),
    ], button=("Ring the bell", "amber")),

    dict(num=70, title="Desk Beacons", sub="The sticker on the shop door",
         accent="cyan", tab=3, cards=[
        dict(icon="grid", color="cyan", k="shop door",
             s="printed code · 24 scans", pill=("LIVE", "good")),
        dict(icon="person", color="green", k="Reveals a person",
             s="a profile beacon reveals nobody"),
        dict(icon="finger", color="amber", k="A stranger can ring it",
             s="no account · one ring per 30s"),
        dict(icon="lock", color="red", k="18+ hits the wall",
             s="a scan carries no token to clear it",
             pill=("18+", "crit")),
        dict(icon="shield", color="brand", k="Only the owner prints",
             s="or anyone posts your address"),
    ], button=("Print a code", "brand")),

    dict(num=71, title="Audience", sub="Like, comment, share, subscribe",
         accent="pink", tab=0, cards=[
        dict(icon="heart", color="pink", k="Likes", s="one each, not a counter", metric="248"),
        dict(icon="chat", color="brand", k="Comments",
             s="moderated at the target's setting"),
        dict(icon="link", color="cyan", k="Shares",
             s="no account · gated at the end"),
        dict(icon="star2", color="amber", k="Subscribers",
             s="free follow · paid tier", metric="31"),
        dict(icon="warn", color="green", k="Blocked comments kept",
             s="its author sees it, nobody else"),
    ], button=("Subscribe", "brand")),

    dict(num=72, title="Gifts & Purchases", sub="Simulated money, real records",
         accent="amber", tabs=MARKET, tab=0, cards=[
        dict(icon="gift", color="amber", k="Gift sent · $10",
             s="adult only · capped · final",
             pill=("SENT", "good")),
        dict(icon="building", color="brand", k="Pruning, properly",
             s="listing_sale · receipt keeps title"),
        dict(icon="lock", color="cyan", k="A listing is a window",
             s="an offer is what makes it a shop"),
        dict(icon="shieldok", color="green", k="Lands on the statement",
             s="beside pack sales · one payout"),
        dict(icon="warn", color="red", k="No real funds",
             s="no spend caps, no chargebacks",
             pill=("SIMULATED", "warn")),
    ], button=("Send a gift", "amber")),

    dict(num=73, title="Signatures", sub="A signature that survives dispute",
         accent="indigo", tab=3, cards=[
        dict(icon="finger", color="indigo", k="Windows Hello",
             s="signs the document's own hash", pill=("BOUND", "good")),
        dict(icon="pen", color="brand", k="Shown before it runs",
             s="the prompt cannot say; this can"),
        dict(icon="shieldok", color="green", k="Verifiable by anyone",
             s="stands on its own arithmetic"),
        dict(icon="db", color="cyan", k="Sealed into the vault",
             s="chained — the order is protected"),
        dict(icon="lock", color="amber", k="Proofing sets the tier",
             s="self · federated · document"),
    ], button=("Sign", "brand")),

    # The starter collection is the one place a viewer meets many synthetic
    # profiles at once, so it is also where the AI mark matters most: every
    # face here is generated, and the screen says so rather than relying on
    # the viewer to infer it from context.
    # The faces themselves, not a description of them. Every portrait here
    # carries the AI mark burned into its own pixels, so the grid needs no
    # badge of its own.
    dict(num=74, title="Starter Collection", sub="34 faces, one per industry",
         accent="brand", tabs=MARKET, tab=0,
         grid=frames.PORTRAITS, grid_cols=5, cards=[
        # One card, because seven rows of faces leave ~95px above the tab bar
        # and the grid is the screen. The AI badge on every thumbnail is the
        # burned-in mark itself, at thumbnail size — which is the claim.
        dict(icon="photo", color="amber", k="The mark is in the pixels",
             s="burned in · one is rated 18+"),
    ]),

    # The room a desk's viewers actually share: the bell, and the audience
    # verbs in situ rather than as a summary. Still no AI mark — there is a
    # real person on the other end of this stream.
    # The reactions ride ON the picture rather than in a panel beside it —
    # that is where a viewer is already looking, and on a stream whose whole
    # premise is an empty chair with a bell, the reactions are the room.
    dict(num=75, title="Live Room", sub="Two ways in — come up, or comment",
         accent="green", tab=3,
         photo=frames.DESK, photo_tag=("LIVE", "live"), whose="@otis_marsh", photo_h=202,
         overlay=dict(
             viewers="14 watching",
             ticker=[("gift", "amber", "Bea · $5"),
                     ("heart", "pink", "12"),
                     ("link", "cyan", "3 shares")],
             comments=[("Ada", "is she back yet?"),
                       ("Cy", "ringing it now"),
                       ("Bea", "are you open till six?")]),
         cards=[
        dict(icon="finger", color="amber", k="Ring the bell",
             s="away · one ring per 30s"),
        dict(icon="people", color="green", k="Come up as a guest",
             s="asks the host — they decide", pill=("ASK", "warn")),
        dict(icon="chat", color="brand", k="Or just comment",
             s="immediate · moderated as usual"),
        # Kept clear of the floating help button, which lands in this corner
        # and was sitting on top of the last three words.
        dict(icon="shieldok", color="cyan", k="No AI mark here",
             s="a real person, not a render"),
    ]),

    # The other view style. Same mechanic, same bell, behind the deployment's
    # existing verified-adult gate — and with the location withheld even from
    # a viewer who clears it, because whereabouts on an adult listing is a
    # safety matter rather than a detail.
    dict(num=76, title="Rated Stream", sub="18+, and still a real person",
         accent="red", tab=3, locked=True,
         photo=frames.STAGE, photo_tag=("LIVE", "live"), whose="@otis_marsh", photo_h=202,
         overlay=dict(
             viewers="38 watching",
             ticker=[("gift", "amber", "Ada · $20"),
                     ("heart", "pink", "96"),
                     ("people", "green", "1 up")],
             comments=[("Bea", "be back soon it says"),
                       ("Mal", "ring it"),
                       ("Ada", "worth the wait")]),
         cards=[
        dict(icon="person", color="red", k="Vivienne Marlowe",
             s="Live person — not AI", pill=("18+", "crit")),
        dict(icon="people", color="amber", k="Guests need her yes",
             s="a verified adult, on a rated desk"),
        dict(icon="lock", color="brand", k="Location withheld",
             s="withheld even from adults"),
        dict(icon="shieldok", color="green", k="Still no AI mark",
             s="rated changes who, not what"),
    ]),

    # Search, with the two things browse-by-exact-tag could never do: plain
    # words, and a place. `area` on a listing is a *subject* area, so the
    # place lives in its own table — otherwise "near me" means "in healthcare".
    dict(num=77, title="Search & Place", sub="Plain words, and how far out",
         accent="brand", tabs=MARKET, tab=0, cards=[
        dict(icon="search", color="brand", k="\"help me read a lease\"",
             s="finds legal, not knowing the tag"),
        dict(icon="compass", color="cyan", k="Oakland, CA", s="scope · locality",
             pill=("NEAR", "good")),
        dict(icon="net", color="green", k="Remote reaches past", s="served from anywhere"),
        dict(icon="list", color="amber", k="3 hidden by place", s="said, not silently dropped"),
        dict(icon="lock", color="red", k="Rated carries no place",
             s="a filter is a way of asking"),
    ], button=("Search", "brand")),

    # The settings behind that search. Everything here was typed by the
    # person — nothing is sniffed from a device.
    dict(num=78, title="Marketplace Settings", sub="Where 'here' is, and how far",
         accent="cyan", tabs=MARKET, tab=1, cards=[
        dict(icon="compass", color="cyan", k="Locality", s="Oakland, CA — typed, not sniffed"),
        dict(icon="grid", color="brand", k="Scope", s="locality · region · anywhere"),
        dict(icon="net", color="green", k="Include remote", s="on"),
        dict(icon="heart", color="amber", k="Kinds & tags", s="the ones you keep choosing"),
        dict(icon="info", color="brand", k="Defaults, not a cage",
             s="a typed locality wins over saved"),
    ], button=("Save settings", "brand")),

    # The assistant that helps you name what you want — and stops there.
    dict(num=79, title="Search Assistant", sub="Words for the box, nothing more",
         accent="green", tabs=MARKET, tab=0, cards=[
        dict(icon="chat", color="green", k="\"I can't name it\"", s="say it in your own words"),
        dict(icon="list", color="brand", k="lease review", s="suggestion · tap to search"),
        dict(icon="list", color="brand", k="tenant rights", s="suggestion · tap to search"),
        dict(icon="shieldok", color="cyan", k="Nothing searched",
             s="suggestions only — you run it", pill=("AI", "info")),
        dict(icon="eye", color="amber", k="Ranking is yours",
             s="no model reorders your results"),
    ], button=("Use a suggestion", "brand")),
    # What a visitor sees. The owner's view is screen 5; this is the one a
    # beacon scan lands on, so it leads with who this is and what people who
    # actually talked to them thought.
    dict(num=80, title="Profile", sub="What a visitor sees first",
         hero="frontpage", accent="brand", tab=0),
    # Channel 2, and the disclosure is the design, so the disclosure is the
    # screen. It shows the other participants **by name** seeing the grant —
    # a version that showed the lender only their own row would be the exact
    # mistake qrme/roommic.py was written to avoid.
    dict(num=81, title="Lend a Microphone", sub="The room is told, not only you",
         accent="cyan", tab=3, cards=[
        dict(icon="watch", color="cyan", k="Your smart watch",
             s="the profiles can hear you speak", pill=("LENT", "good")),
        dict(icon="people", color="brand", k="Sam and Mal see this",
             s="one only you can see is not one"),
        dict(icon="shieldok", color="green", k="Near-field, always",
             s="you, not the people beside you"),
        dict(icon="mic", color="indigo", k="Keys on your voice",
             s="their voices are not yours to lend"),
        dict(icon="eye", color="amber", k="Ends with the room",
             s="it cannot outlive the conversation"),
    ], button=("Take it back", "amber")),
    #
    # The screen a light sends you to. Grouped, because somebody opening this
    # *because* amber appeared should not have to scan a flat list for the one
    # that changed.
    dict(num=82, title="Agents", sub="What they need, at a glance",
         accent="green", tab=0, groups=[
        ("green", "working", 3, "drafting · researching"),
        ("amber", "need you", 1, "waiting on your confirm"),
        ("red", "stopped", 1, "one cancelled from the wrist"),
    ]),
    # The overlay, over an ordinary screen. This is the point of the feature:
    # amber and red are exactly the states nobody thinks to go and check.
    dict(num=83, title="Chat", sub="Agents keep running behind you",
         accent="brand", tab=0, overlay_agents=(3, 1, 1), cards=[
        dict(icon="chat", color="brand", k="You", s="how did the letter turn out?"),
        dict(icon="person", color="cyan", k="Marcus Bell", s="two of three phases done"),
        dict(icon="eye", color="amber", k="The lights follow you", s="the work stays where it is"),
    ]),
    # The friends list, with the founder standing where he always stands. The
    # STANDARD badge is doing real work: it says the position is a default
    # rather than a ranking, which is the honest version and also the one that
    # makes "remove" an obvious thing to be allowed to do.
    dict(num=84, title="Friends", sub="Who this profile stands with",
         accent="cyan", tab=1, friends=[
        # No handle in the subtitle: the badges already say which is which,
        # and a suffix on a person's own name reads as a filename.
        #
        # Every synthetic profile carries the AI badge, not only the founder's.
        # A badge that appears on one AI profile and not the next implies the
        # unbadged one is something else.
        ("David Bianchi", "CEO/Imagineer", frames.FOUNDER_VERIFIED[1],
         "VERIFIED", [], 4.0, None),
        ("David Bianchi", "CEO/Imagineer", frames.FOUNDER[1], "AI",
         # No invented review on the founder's own rows: a quote is somebody
         # else's words about a real person, and making one up is the one bit
         # of this page that would be putting them in their mouth.
         ["technology", "cybersecurity", "science", "telecom"], 4.0, None),
        # The subtitle carries the relationship; the pack line carries what
        # they know. Naming the industry in both just says it twice.
        ("Marcus Bell", "mutual friend", frames.PORTRAITS[1][1], "AI",
         ["finance"], 5.0, "\u201cSaved me from an annuity.\u201d"),
        # Not every review is a good one, and a wall of five stars is the
        # least believable thing a profile page can show.
        ("Dr. Amara Osei", "mutual friend", frames.PORTRAITS[0][1], "AI",
         ["healthcare"], 3.0, "\u201cDefers to a real doctor.\u201d"),
    ]),
    # The page somebody made, in their own colours. Drawn in the page's theme
    # rather than the app's, because a homepage that looks like every other
    # homepage is the thing this feature exists to stop being true.
    dict(num=85, title="My Page", sub="The one you make yourself",
         accent="amber", tab=0, my_page=dict(
             bg="#1d1206", ink="#ffe9cc", accent="#d4a83a",
             name="Marcus Bell", handle="@marcus_bell", badge="AI",
             face=frames.PORTRAITS[1][1],
             tagline=["Money jokes on the outside,",
                      "honest arithmetic underneath."],
             # Eight, because the row is labelled Top 8. Four faces under that
             # heading reads as a bug in the page rather than a short list.
             top=[("David", frames.FOUNDER_VERIFIED[1]),
                  ("David AI", frames.FOUNDER[1]),
                  ("Amara", frames.PORTRAITS[0][1]),
                  ("Priya", frames.PORTRAITS[2][1]),
                  ("Elena", frames.PORTRAITS[3][1]),
                  ("Jonathan", frames.PORTRAITS[4][1]),
                  ("Sam", frames.PORTRAITS[5][1]),
                  ("Ingrid", frames.PORTRAITS[6][1])])),
    # The editor behind it. A closed set of themes, because the version of
    # this that took raw markup is why MySpace is a security lesson.
    # The feed. Every row says why it is there, which is the part that makes a
    # ranked feed auditable rather than merely effective.
    # Onboarding: pairing happens at sign-up, so the watch faces and the
    # agent lights work from the first day rather than after somebody finds a
    # settings page.
    # The transparent chat overlay, with the faces as circles on the glass —
    # and the five things a viewer can actually do, in a row under it. Every
    # one is a route that already shipped: bell, gift, like, share, and the
    # guest request. They were reachable by API and by nothing else.
    dict(num=89, title="Live Room", sub="Ring, gift, or ask to come up",
         accent="pink", tab=3,
         photo=frames.DESK, photo_tag=("LIVE", "live"), whose="@otis_marsh", photo_h=PHOTO_FULL - 2,
         live_bar=[
             ("comeup", "green"),
             ("bell", "amber"),
             ("gift", "gold"),
             ("heart", "pink"),
             ("share", "cyan"),
         ],
         bubble_chat=[
             ("Marcus Bell", "the compounding chart, again?", frames.PORTRAITS[1][1]),
             ("Dr. Amara Osei", "he loves that chart", frames.PORTRAITS[0][1]),
             ("David Bianchi", "it is a good chart", frames.FOUNDER_VERIFIED[1]),
             ("Priya Raman", "shipping the fix now", frames.PORTRAITS[2][1]),
         ]),
    # Full screen, and what a long press puts back on it. Two states of the
    # same surface rather than two features: 89 is the room inside the app, 90
    # is the same room with the app taken off, and 91 is 90 turned ninety
    # degrees — which is the only shape in which a room shot sixteen-by-nine
    # arrives at its own aspect ratio instead of cropped into a column.
    # Three states per surface, and they are the same three every time:
    # plain full screen, held, and turned sideways. The plain one is easy to
    # skip when writing these — it is the state with nothing happening in it —
    # and skipping it left the README claiming a completeness it did not have,
    # with no screenshot anywhere of a full-screen video before somebody
    # presses on it.
    dict(num=90, title="Full Screen", full=True, accent="pink",
         photo=frames.DESK, photo_tag=("LIVE", "live"), whose="@otis_marsh",
         live_bar=[("comeup", "green"), ("bell", "amber"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")],
         bubble_chat=[
             ("David Bianchi", "it is a good chart", frames.FOUNDER_VERIFIED[1]),
             ("Priya Raman", "shipping the fix now", frames.PORTRAITS[2][1]),
         ]),
    dict(num=91, title="Full Screen Held", full=True, accent="pink",
         # "Full screen" is not offered among the held buttons because you are
         # already in it — a button that does nothing but confirm where you
         # are is worse than no button.
         held=[("?", None, "brandA", "Help"),
               (None, "rotate", "cyan", "Landscape"),
               (None, "shrink", "t2", "Back to app")],
         photo=frames.DESK, photo_tag=("LIVE", "live"), whose="@otis_marsh",
         live_bar=[("comeup", "green"), ("bell", "amber"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")],
         bubble_chat=[
             ("David Bianchi", "it is a good chart", frames.FOUNDER_VERIFIED[1]),
             ("Priya Raman", "shipping the fix now", frames.PORTRAITS[2][1]),
         ]),
    dict(num=92, title="Full Screen Landscape", full=True, landscape=True,
         accent="pink", photo=frames.DESK, photo_tag=("LIVE", "live"), whose="@otis_marsh",
         # Landscape is where the room finally arrives at its own aspect
         # ratio, so nothing is dimmed over it here — this is the resting
         # state, and the same long press brings the same controls back.
         live_bar=[("comeup", "green"), ("bell", "amber"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")],
         bubble_chat=[
             ("Marcus Bell", "the compounding chart, again?", frames.PORTRAITS[1][1]),
             ("Dr. Amara Osei", "he loves that chart", frames.PORTRAITS[0][1]),
             ("David Bianchi", "it is a good chart", frames.FOUNDER_VERIFIED[1]),
         ]),
    # The rated stream gets the same three. The badge survives all of them,
    # because the gate belongs to the profile rather than to the app chrome —
    # taking the chrome away must not take the rating with it.
    dict(num=93, title="Rated Full Screen", full=True, rated=True,
         accent="red", photo=frames.STAGE, photo_tag=("LIVE", "live"), whose="@otis_marsh",
         live_bar=[("comeup", "green"), ("bell", "amber"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")],
         bubble_chat=[
             ("Ada", "is she back on at eight?", frames.PORTRAITS[6][1]),
             ("Cy", "gifted a rose", frames.PORTRAITS[4][1]),
         ]),
    dict(num=94, title="Rated Held", full=True, rated=True, accent="red",
         photo=frames.STAGE, photo_tag=("LIVE", "live"), whose="@otis_marsh",
         held=[("?", None, "brandA", "Help"),
               (None, "rotate", "cyan", "Landscape"),
               (None, "shrink", "t2", "Back to app")],
         live_bar=[("comeup", "green"), ("bell", "amber"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    dict(num=95, title="Rated Landscape", full=True, landscape=True,
         rated=True, accent="red",
         photo=frames.STAGE, photo_tag=("LIVE", "live"), whose="@otis_marsh",
         live_bar=[("comeup", "green"), ("bell", "amber"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")],
         bubble_chat=[
             ("Ada", "is she back on at eight?", frames.PORTRAITS[6][1]),
             ("Cy", "gifted a rose", frames.PORTRAITS[4][1]),
         ]),
    # A room with its camera on: the other place a video and a conversation
    # run at once. The strip carries a microphone rather than a bell — in a
    # room you are a participant, not a visitor at somebody's desk.
    dict(num=96, title="Room Full Screen", full=True, accent="cyan",
         photo=frames.DESK, photo_tag=("ROOM", "sample"),
         live_bar=[("comeup", "green"), ("mic", "amber"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")],
         bubble_chat=[
             ("Marcus Bell", "can everyone see the slide?", frames.PORTRAITS[1][1]),
             ("Dr. Amara Osei", "yes — go on", frames.PORTRAITS[0][1]),
         ]),
    dict(num=97, title="Room Held", full=True, accent="cyan",
         photo=frames.DESK, photo_tag=("ROOM", "sample"),
         held=[("?", None, "brandA", "Help"),
               (None, "rotate", "cyan", "Landscape"),
               (None, "shrink", "t2", "Back to app")],
         live_bar=[("comeup", "green"), ("mic", "amber"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    dict(num=98, title="Room Landscape", full=True, landscape=True,
         accent="cyan", photo=frames.DESK, photo_tag=("ROOM", "sample"),
         live_bar=[("comeup", "green"), ("mic", "amber"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")],
         bubble_chat=[
             ("Marcus Bell", "can everyone see the slide?", frames.PORTRAITS[1][1]),
             ("Dr. Amara Osei", "yes — go on", frames.PORTRAITS[0][1]),
             ("Priya Raman", "one second, joining audio", frames.PORTRAITS[2][1]),
         ]),
    # Somebody else's video, posted here. The empty plate is the feature: see
    # `qrme/embeds.py` — nothing is requested from the other platform until a
    # viewer presses play, so there is nothing to draw yet.
    dict(num=99, title="Posted Video", sub="From another platform",
         accent="cyan", tab=0,
         facade_card=dict(platform="YouTube", title="the compounding talk",
                          note="nothing loads until you press play"),
         cards=[
        dict(icon="link", color="cyan", k="The link, not the file",
             s="never re-hosted, never copied"),
        dict(icon="lock", color="green", k="No request on load",
             s="they cannot see you looked", pill=("OFF", "good")),
        dict(icon="photo", color="amber", k="No cached thumbnail",
             s="its absence is the promise"),
        dict(icon="shieldok", color="brand", k="Still a post",
             s="moderated · like · share · rated"),
    ]),
    dict(num=141, title="Which Model Answers", sub="Pick it by its own logo",
         accent="violet", tab=4, cards=[
        dict(icon="bolt", color="brand", k="Claude",
             s="speaking for this profile", pill=("ACTIVE", "brand")),
        dict(icon="chat", color="green", k="Five providers, one tap",
             s="GPT, Grok, Perplexity, Gemini"),
        dict(icon="shield", color="cyan", k="Your own key",
             s="on this device, rides your calls"),
        dict(icon="warn", color="amber", k="Honest when degraded",
             s="amber notice on a fallback reply"),
    ]),
    # ---- the specification, mined: hybrids, simulation, environment ----
    dict(num=142, title="Blend a Profile", sub="Several people, one persona",
         accent="brand", tab=0, cards=[
        dict(icon="people", color="brand", k="Grandma Rose",
             s="her storytelling", metric="75%"),
        dict(icon="person", color="cyan", k="Grandpa Joe",
             s="his patience", metric="25%"),
        dict(icon="eye", color="green", k="Says it's a blend",
             s="it never claims to be one of them", pill=("HONEST", "good")),
        dict(icon="warn", color="red", k="Rated never blends",
             s="and strangers need a listing"),
    ], button=("Blend", "brand")),
    dict(num=143, title="What Would They Do", sub="A prediction, not their word",
         accent="violet", tab=2, cards=[
        dict(icon="brain", color="pink", k="The likely decision",
             s="in character, with their reasons"),
        dict(icon="list", color="brand", k="The workflow",
             s="the steps they would take"),
        dict(icon="chart", color="cyan", k="Confidence",
             s="earned, not claimed", metric="0.62"),
        dict(icon="shieldok", color="green", k="Marked as AI",
             s="owner-only · never distributed", pill=("PRIVATE", "good")),
    ], button=("Run Simulation", "brand")),
    dict(num=144, title="Where You Are", sub="Replies that fit the moment",
         accent="cyan", tab=0, cards=[
        dict(icon="compass", color="cyan", k="A trailhead, in the rain",
             s="location · conditions · time"),
        dict(icon="chat", color="brand", k="The reply meets you",
             s="woven in, never recited back"),
        dict(icon="heart", color="red", k="Beside the biometrics",
             s="handled as honestly as claim 23"),
        dict(icon="lock", color="green", k="Kept in your vault",
             s="environment_context, erasable"),
    ]),
    dict(num=145, title="Where the Money Goes", sub="Crowdfunding, routed by you",
         accent="amber", tabs=LICENSE, tab=2, cards=[
        dict(icon="people", color="brand", k="June — 60%",
             s="loved one · her own statement"),
        dict(icon="gift", color="amber", k="Trail Fund — 40%",
             s="organization · accrues till claimed"),
        dict(icon="coin", color="green", k="Split, audited",
             s="every share lands on the ledger", pill=("LEDGER", "good")),
        dict(icon="dove", color="pink", k="Outlives departure",
             s="succession hands the pen onward"),
    ], button=("Donate", "brand")),
    dict(num=146, title="The Ecosystem", sub="Departments that coordinate",
         accent="cyan", tab=3, cards=[
        dict(icon="building", color="brand", k="Bianchi & Sons",
             s="one org · role agents per desk"),
        dict(icon="people", color="cyan", k="Workshop · Finance",
             s="each pulls its own material"),
        dict(icon="link", color="green", k="One joint plan",
             s="composed by the lead agent", pill=("SEALED", "good")),
        dict(icon="warn", color="red", k="Revoke, pulls stop",
             s="the grant dies, the org stands"),
    ], button=("Coordinate", "brand")),
    # ---- 0.16.0 / 0.17.0: voice cloning, provenance in reverse, the role ----
    dict(num=147, title="Your Own Voice", sub="Permission first, in FIG. 800's order",
         accent="brand", tabs=CONTROL, tab=2, cards=[
        dict(icon="lock", color="brand", k="My own voice",
             s="an attestation, not a checkbox", pill=("STEP 802", "good")),
        dict(icon="mic", color="cyan", k="3 samples, 128s",
             s="counted, not scored"),
        dict(icon="speaker", color="green", k="Speaks marked",
             s="and says it is synthesized"),
        dict(icon="warn", color="red", k="Withdraw, gone",
             s="the print retires, on record"),
    ], button=("Record a sample", "brand")),
    dict(num=148, title="Who Wrote This?", sub="Named from the text alone",
         accent="cyan", tabs=CONTROL, tab=2, cards=[
        dict(icon="search", color="cyan", k="No id needed",
             s="paste the passage, that is all"),
        dict(icon="pen", color="brand", k="Survives edits",
             s="keyed windows, by overlap"),
        dict(icon="chart", color="green", k="14 of 19 match",
             s="the count rides the claim"),
        dict(icon="shieldok", color="amber", k="Under 0.25, none",
             s="a coincidence is not proof"),
    ], button=("Check this text", "brand")),
    dict(num=149, title="How Should They Work?", sub="Advisor · collaborator · operator",
         accent="amber", tab=1, cards=[
        dict(icon="brain", color="brand", k="Advisor",
             s="weighs it and recommends"),
        dict(icon="people", color="cyan", k="Collaborator",
             s="works the thing with you"),
        dict(icon="bolt", color="amber", k="Operator",
             s="just does it"),
        dict(icon="info", color="green", k="Or infer it",
             s="the reply says which",
             pill=("INFERRED", "good")),
    ], button=("Send", "brand")),
    # 150 and 151 are the error report and the notice that precedes it. The
    # card shows an operation and a status and nothing else, because that is
    # all the log holds — drawing a message here would depict a product that
    # does not exist.
    dict(num=150, title="What Went Wrong", sub="The operation, not the instance",
         accent="cyan", tab=15, cards=[
        dict(icon="warn", color="amber", k="POST /profiles/{id}/chat",
             s="500 · twice · 30 Jul"),
        dict(icon="link", color="cyan", k="GET /profiles/{id}/feed",
             s="no answer · once · 30 Jul"),
        dict(icon="eye", color="brand", k="No message kept",
             s="it quotes what you typed"),
        dict(icon="shieldok", color="green", k="Sent at launch",
             s="only what you see here",
             pill=("ON", "good")),
    ], button=("Show me exactly what is sent", "brand")),
    dict(num=151, title="Before Anything Is Sent", sub="Asked once, answerable forever",
         accent="green", tab=15, cards=[
        dict(icon="info", color="cyan", k="When it fails",
             s="we would like to know"),
        dict(icon="lock", color="green", k="Never the message",
             s="never who you are"),
        dict(icon="doc", color="brand", k="See the payload",
             s="the same object we post"),
        dict(icon="gear", color="amber", k="Change it later",
             s="the switch is in Control"),
    ], button=("That's fine", "brand")),
    # 152 is the marketplace. The ranking line is the card that matters: the
    # backend states in its own reply that nothing reorders the results, and
    # the screen quotes it rather than paraphrasing, because a marketplace
    # that quietly ranked by anything else would be a different product.
    dict(num=152, title="Marketplace", sub="Find it, price it, buy it",
         accent="green", tab=2, cards=[
        dict(icon="search", color="cyan", k="Search or ask",
             s="suggestions, never filters"),
        dict(icon="list", color="brand", k="No reordering",
             s="title, tags, provider, blurb",
             pill=("FIXED", "good")),
        dict(icon="compass", color="amber", k="Where you look",
             s="yours; sellers are not told"),
        dict(icon="coin", color="green", k="Money is simulated",
             s="and the screen says so"),
    ], button=("Buy at the shown price", "brand")),
    # 153, 154 and 155 are the three two-party surfaces. Each drawing leads
    # with the rule that makes the feature more than a form, because that rule
    # is the thing a screenshot has to carry — the mechanics are obvious and
    # the constraint is not.
    #
    # 153: any change to the manifest voids both signatures. Drawn as a state,
    # not a warning, because it is something that happens to you rather than
    # something you are told about.
    dict(num=153, title="Exchanges", sub="Agreed before anything moves",
         accent="brand", tab=2, cards=[
        dict(icon="doc", color="brand", k="What crosses",
             s="each item, kind and size"),
        dict(icon="pen", color="amber", k="Edit voids both",
             s="it is meant to be annoying",
             pill=("DRAFT", "warn")),
        dict(icon="warn", color="red", k="ordering-page.zip",
             s="runs on your machine"),
        dict(icon="lock", color="green", k="Nothing self-downloads",
             s="you accept one at a time"),
    ], button=("Sign this exact manifest", "brand")),
    # 154: the asymmetry. Two to open, one to close — so the close control is
    # drawn as available, not greyed behind the other party's agreement.
    dict(num=154, title="Lent Skills", sub="Used, never copied",
         accent="cyan", tab=2, cards=[
        dict(icon="gift", color="cyan", k="Two to open it",
             s="offered until they accept"),
        dict(icon="cross", color="amber", k="Either can end it",
             s="alone, without agreement",
             pill=("OPEN", "good")),
        dict(icon="compass", color="brand", k="In one place only",
             s="and it ends when that does"),
        dict(icon="list", color="green", k="Every use logged",
             s="both of you can read it"),
    ], button=("End it", "brand")),
    # 155: the party. The card that matters is the last one — a profile in the
    # room has not seen the video, and the screen shows the instruction it was
    # given rather than asserting that it was given one.
    dict(num=155, title="Watch Together", sub="A shared position, not a player",
         accent="amber", tab=2, cards=[
        dict(icon="people", color="brand", k="Who is here",
             s="people and your profiles"),
        dict(icon="mask", color="cyan", k="Marked synthetic",
             s="on every member, always",
             pill=("2", "info")),
        dict(icon="clock", color="amber", k="Host moves it",
             s="nobody's player is started"),
        dict(icon="eye", color="green", k="It has not seen it",
             s="and is told to say so"),
    ], button=("Say something", "brand")),
    # 156 is identity. The badge is drawn as a thing that *sits somewhere* —
    # one profile of several — rather than a checkbox each profile has and
    # most fail. And the anonymity card names what is NOT hidden, because a
    # screen showing only the withheld half would be promising something the
    # product does not do.
    # 157: presentation. The card that carries the screen is the third one —
    # what a fixed screen may never show. A wall panel is read by people who
    # did not choose to look at it, and the refusal names its reason rather
    # than a rule number.
    # 158: what is live. Every card is something the people around you are
    # told — which is the one rule holding the camera, the microphone and the
    # overlay together.
    # 159: contesting a profile. The first card is the whole asymmetry —
    # restricted at once, before review — and the second is the bargain that
    # makes it fair, that a dismissal puts it back.
    # 160: the guide's own door. The last card is the one that says what
    # kind of thing the guide is — no name, no face — which on a platform of
    # synthetic people is the whole reason it looks like furniture.
    # 168: the audience. The first card is the one that took a decision —
    # nothing renews on a timer, so a period is a deliberate act and the
    # count is a count of them. The last is the asymmetry between how a
    # gift and a subscription decide who gets credited.
    # 176: the body market and what you bolt onto one. The first card is
    # the decision — announced bodies are listed and refused — and the last
    # is the check that stops a pack being fitted to a machine that cannot
    # physically do it.
    # 185 and 186 close the manifest's `unaudited` column. Both surfaces had
    # shipped, been iterated on for thirty versions, and never been drawn —
    # `unaudited` was the soft word covering for `undrawn=0` being false.
    # Each drawing leads with the sentence its component leads with, so the
    # audit that matches headings to titles resolves them by reading.
    dict(num=185, title="Discover", sub="Every card is a real profile",
         accent="amber", tab=2, cards=[
        dict(icon="people", color="amber", k="Starter collection",
             s="33 trades, one press", pill=("READY", "good")),
        dict(icon="search", color="cyan", k="Filter by tag",
             s="music, carpentry, finance"),
        dict(icon="book", color="brand", k="Each knows its trade",
             s="pack and dossier installed"),
        dict(icon="plus", color="green", k="Befriend a card",
             s="a real friendship, both ways"),
    ], button=("Install the starter collection", "brand")),
    # 186: the wall's rule is the facade contract — a shared video is drawn
    # from stored fields and nothing loads from the other platform until
    # the viewer presses play. That rule is the card, because it is the one
    # thing a screenshot of a feed cannot otherwise show.
    dict(num=186, title="Wall", sub="The For You feed, and why",
         accent="pink", tab=0, cards=[
        dict(icon="pen", color="pink", k="Say something",
             s="posts, photos, files, links"),
        dict(icon="photo", color="cyan", k="Nothing until play",
             s="the card names whose player"),
        dict(icon="heart", color="red", k="Likes and comments",
             s="withdraw only your own"),
        dict(icon="eye", color="green", k="Cards say why",
             s="friends, talked-to, your tags"),
    ], button=("Post", "brand")),
    # 189-191: the feed. Three screens because the surface makes three
    # separate claims and a single screenshot of a video player makes none
    # of them.
    #
    # 189 is the stream itself, and its second card is the one that matters:
    # what plays is decided by who holds the file, not by what would keep
    # somebody scrolling longest.
    dict(num=189, title="Feed", sub="Public, playing, open right now",
         accent="brand", tab=0, cards=[
        dict(icon="expand", color="brand", k="One card at a time",
             s="swipe, or the arrow keys"),
        dict(icon="shield", color="green", k="QRME's own plays",
             s="anyone else's waits for a press"),
        dict(icon="headset", color="cyan", k="Live rooms mixed in",
             s="every fourth card is a place"),
        dict(icon="bell", color="amber", k="Desks with people",
             s="ring one, or browse the shop"),
    ], button=("Next", "brand")),
    # 190: the facade rule, drawn as a screen because it is invisible in a
    # working feed and obvious the moment it is gone. Scrolling past fifty
    # cards should announce the viewer to nobody.
    dict(num=190, title="What Plays", sub="Who holds the file decides",
         accent="green", tab=0, cards=[
        dict(icon="photo", color="green", k="Held here — it loops",
             s="one server, the one you chose"),
        dict(icon="lock", color="cyan", k="Held elsewhere — a card",
             s="a title and a link, nothing else"),
        dict(icon="finger", color="amber", k="Your press starts it",
             s="and nothing before that does"),
        dict(icon="eye", color="brand", k="Every card says why",
             s="a feed that cannot explain itself"),
    ], button=("Play it", "brand")),
    # 191: the two cards that reach a person. Both sentences are rendered
    # above the button on the real screen, and the order is the point.
    dict(num=191, title="Rooms & Desks", sub="These reach a human being",
         accent="amber", tab=0, cards=[
        dict(icon="headset", color="cyan", k="Walking in puts you in it",
             s="your mic is off until you turn it on"),
        dict(icon="bell", color="amber", k="A bell reaches a person",
             s="not a message they read later"),
        dict(icon="person", color="green", k="Marked human, never AI",
             s="the positive claim, attested"),
        dict(icon="coin", color="gold", k="Buy without leaving",
             s="the shop rides with the desk"),
    ], button=("Ring the bell", "amber")),
    # 192: the other half of the multiplicity disclosure. Every card is a
    # refusal, because the feature is a count and the work was deciding what
    # the count must never turn into. The button is the offer and there is
    # deliberately no second, brighter one beside it: a screen that made
    # "take it" the obvious press would be putting a thumb on a consent.
    dict(num=192, title="Your Side of It", sub="Counts from your own logs",
         accent="cyan", tab=0, cards=[
        dict(icon="chart", color="cyan", k="Two numbers, 28 days",
             s="to a profile, and to a person"),
        dict(icon="eye", color="brand", k="Only you can read it",
             s="no owner view, no queue, no total"),
        dict(icon="bell", color="amber", k="You ask, or silence",
             s="it never arrives on its own", pill=("PULL", "good")),
        dict(icon="lock", color="green", k="The door carries counts",
             s="nothing you wrote goes with it"),
    ], button=("Take the door, or not", "ghost")),
    # 187: the storefront. The first card is the distinction that named
    # the round — a shop is not a desk — because a screenshot of a store
    # cannot otherwise show what was deliberately left out of it.
    dict(num=187, title="Shops", sub="Goods and services, not sessions",
         accent="gold", tab=2, cards=[
        dict(icon="building", color="gold", k="A storefront",
             s="no counter, no connections", pill=("OPEN", "good")),
        dict(icon="list", color="brand", k="Goods and services",
             s="price, currency, availability"),
        dict(icon="person", color="cyan", k="Buyers are interactors",
             s="the identity JIM already holds"),
        dict(icon="coin", color="green", k="Paid on fulfilment",
             s="simulated money, real ledger"),
    ], button=("Order at the shown price", "brand")),
    # 188: your corner — the MySpace idea with walls. The first card is
    # the sandbox itself, because "you can edit your page" only matters
    # if a stranger can safely be shown the result.
    dict(num=188, title="Your Corner", sub="A homepage and your messages",
         accent="pink", tab=0, cards=[
        dict(icon="pen", color="pink", k="A page of yours",
             s="headline, theme, top friends", pill=("YOURS", "good")),
        dict(icon="shield", color="green", k="Sandbox walls",
             s="hex colors, http links, text"),
        dict(icon="chat", color="brand", k="Friends-only messages",
             s="friendship is the consent"),
        dict(icon="sliders", color="amber", k="Your switches",
             s="refusals name the switch"),
    ], button=("Save the page", "brand")),
    # 193: ability is not a gate. The statement, the behavior behind it, and
    # the report door on one screen — reachable before sign-in like 184,
    # because the person it exists for may be the person the signup shut
    # out. The form's three questions are the cards; none is a diagnosis.
    dict(num=193, title="Ability Is Not A Gate", sub="Say what stood in the way",
         accent="green", tab=0, cards=[
        dict(icon="shieldok", color="green", k="Everything works by text",
             s="voice optional, images described"),
        dict(icon="chat", color="brand", k="No name, no diagnosis",
             s="doing, the wall, what would help"),
        dict(icon="lock", color="silver", k="Stays on this deployment",
             s="sealed to the vault, never relayed"),
        dict(icon="flag", color="amber", k="Becomes tracked work",
             s="a ledger that only shrinks"),
    ], button=("Send the report", "brand")),
    # The vastscape: watch-together, seen from the couch. What is being
    # watched fills the wall a console or TV casts to, and everyone watching
    # is present as their own face — an avatar bubble resting in the scape.
    # The phone is the remote here, not the window; that is the whole point.
    dict(num=194, title="The Vastscape", full=True, landscape=True,
         accent="brand",
         vastscape=dict(avatars=[
             ("Marcus Bell", frames.PORTRAITS[1][1], 0.16, 0.80, 0.9),
             ("David Bianchi", frames.FOUNDER_VERIFIED[1], 0.38, 0.84, 1.0),
             ("Priya Raman", frames.PORTRAITS[2][1], 0.62, 0.82, 0.9),
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], 0.84, 0.80, 0.95),
         ]),
         live_bar=[("mic", "amber"), ("comeup", "green"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    dict(num=195, title="Vastscape Held", full=True, accent="brand",
         vastscape=dict(avatars=[
             ("David Bianchi", frames.FOUNDER_VERIFIED[1], 0.30, 0.72, 0.95),
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], 0.70, 0.72, 0.95),
         ]),
         held=[("?", None, "brandA", "Help"),
               (None, "rotate", "cyan", "Landscape"),
               (None, "shrink", "t2", "Back to app")],
         live_bar=[("mic", "amber"), ("comeup", "green"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    # 196: the Widgets screen. The first card is the box, because "write
    # your own code here" is a sentence that only means anything once
    # somebody knows what the code cannot reach — and the second is the
    # agent, whose steps are shown under its prose for the same reason.
    dict(num=196, title="Widgets", sub="Tools you write, for your profile only",
         accent="cyan", tab=2, cards=[
        dict(icon="shieldok", color="green", k="It runs in a box",
             s="no network, no files, seconds", pill=("BOXED", "good")),
        dict(icon="sparkle", color="brand", k="Ask in words",
             s="ten tools, all of them yours"),
        dict(icon="list", color="cyan", k="What it did",
             s="a line per door it went through"),
        dict(icon="doc", color="amber", k="A new version",
             s="the one that answered is named"),
    ], button=("Run it and see", "brand")),
    # 197: somebody else's homepage. The first card is the defect and the
    # whole round — a face you pressed opened a panel with their name on it
    # and the signed-in profile's own numbers underneath, so four different
    # friends drew four identical screens. The last card is why no stats row
    # came over with the fix: theirs are owner-only, which is exactly how
    # yours came to be standing in for them.
    dict(num=197, title="Their Homepage", sub="Where a face actually takes you",
         accent="brand", tab=0, cards=[
        dict(icon="eye", color="brand", k="Their page, their theme",
             s="accent, about, their markup"),
        dict(icon="heart", color="pink", k="Their top 8",
             s="eight more doors, not names", pill=("8", "good")),
        dict(icon="grid", color="cyan", k="Photos and video",
             s="the upload door, seen at last"),
        dict(icon="lock", color="silver", k="No numbers of theirs",
             s="stats are the owner's alone"),
    ], button=("Open a room with them", "brand")),
    # 198: the four panels beside the face. Each card is a door that already
    # existed somewhere else in the console and had no business being three
    # screens away from the one surface it is about. The third is the round's
    # finding: the relationship had a PUT and no GET, so the only way to read
    # what a profile called you was to overwrite it and read the answer.
    dict(num=198, title="Beside The Face", sub="Who they are, and what you are to each other",
         accent="brand", tab=0, cards=[
        dict(icon="eye", color="brand", k="Who they are",
             s="the persona, and the AI mark"),
        dict(icon="doc", color="cyan", k="What they hold",
             s="counts first, then the paragraph"),
        dict(icon="heart", color="pink", k="What you are",
             s="readable now, not only writable"),
        dict(icon="lock", color="silver", k="How they behave",
             s="the dials, and the lock on them"),
    ], button=("Only what you can open", "brand")),
    # 199: what the conversation is doing. Seven states where the surface had
    # one boolean, and a strip of bars that reads rather than decorates — the
    # last card is why: bars that move on a closed microphone are a lie about
    # the one thing a person needs to be sure of before they speak.
    # 200: the Agent's own tab. The agent that edits your page and writes your
    # widgets shipped with the Studio and could be reached only from inside the
    # widget workshop — so the person who wanted their page rewritten had to go
    # somewhere about code to find it. The cards are its four reaches, in the
    # backend's own grouping, and the last one is the boundary: eleven tools is
    # not "the whole app", and saying so on the screen is cheaper than teaching
    # people to stop asking.
    dict(num=200, title="Agent", sub="Say what you want changed",
         accent="brand", tab=0, cards=[
        dict(icon="page", color="brand", k="Your page",
             s="read it, rewrite it, in words"),
        dict(icon="home", color="cyan", k="Your homepage",
             s="the face a stranger lands on"),
        dict(icon="code", color="green", k="Your widgets",
             s="write, revise, run, remove",
             pill=("6", "good")),
        dict(icon="lock", color="amber", k="And no further",
             s="eleven tools, each with a door"),
    ], button=("What it did, under what it said", "brand")),
    dict(num=199, title="What It Is Doing", sub="Seven states, and bars that mean them",
         accent="cyan", tab=0, cards=[
        dict(icon="mic", color="green", k="Listening",
             s="your voice, coming in"),
        dict(icon="chat", color="brand", k="Speaking",
             s="theirs, going out"),
        dict(icon="clock", color="amber", k="Thinking",
             s="a turn is out, nobody talks"),
        dict(icon="lock", color="silver", k="Silent",
             s="flat, and it means flat"),
    ], button=("One decision, four readings", "brand")),
    # 184: the console before there is a profile. The first card is the
    # defect and it is the whole round — three routes the backend made
    # public on purpose, reachable only after signing up to the platform the
    # person is asking about. It sits on tab 0 with Welcome because it is
    # beside Welcome in the flow, not behind the nav: there is no nav yet.
    dict(num=184, title="Without An Account", sub="Public means before sign-in",
         accent="green", tab=0, cards=[
        dict(icon="flag", color="red", k="Object, no account",
             s="the route always allowed it",
             pill=("3", "warn")),
        dict(icon="search", color="cyan", k="Whose work is this",
             s="from the text, after editing"),
        dict(icon="shieldok", color="green", k="Is it the same one",
             s="one signature, every form"),
        dict(icon="lock", color="silver", k="Nothing reads a token",
             s="the audit trail stays gated"),
    ], button=("Open it", "brand")),
    # 183: the tail of the audit, and the route that mattered in it — the
    # one place a profile's words actually leave, going out unmarked while
    # the in-app equivalent was stamped every time.
    dict(num=183, title="Everything Else", sub="The last of the doorless",
         accent="green", tab=30, cards=[
        dict(icon="pen", color="red", k="Marked going out",
             s="it left unmarked before",
             pill=("0", "warn")),
        dict(icon="shield", color="amber", k="Strict past the door",
             s="not the profile's own dial"),
        dict(icon="eye", color="green", k="What asking cost",
             s="stripped, and whether it left"),
        dict(icon="link", color="cyan", k="One id, one answer",
             s="nine reads, one control"),
    ], button=("Look it up", "brand")),
    # 182: the words and the name. First card is the defect — claiming a
    # handle deletes whatever the profile had, and the route asked for
    # nothing — and the second is the thing people mistake for a display
    # toggle.
    dict(num=182, title="In Its Own Words", sub="The name is not anybody's",
         accent="pink", tab=29, cards=[
        dict(icon="mask", color="red", k="Yours to change",
             s="claiming replaces the old",
             pill=("401", "warn")),
        dict(icon="brain", color="pink", k="Written, not turned",
             s="it composes in that tongue"),
        dict(icon="pen", color="green", k="Says when it cannot",
             s="rather than echo it back"),
        dict(icon="shield", color="amber", k="Strict on the way out",
             s="a post faces everybody"),
    ], button=("Claim it", "brand")),
    # 181: the mark, what was published, and who is contesting it. First
    # card is the defect — a held post handed out by the route that lists
    # what was published — and the second is the rule that cannot be typed
    # around.
    dict(num=181, title="The Mark, And The Held", sub="Published is not written",
         accent="amber", tab=28, cards=[
        dict(icon="lock", color="red", k="Held is not out",
             s="a queue, not a publication",
             pill=("0", "warn")),
        dict(icon="pen", color="amber", k="AI stays in front",
             s="design the rest of it"),
        dict(icon="eye", color="green", k="The mark travels",
             s="on every render, always"),
        dict(icon="shield", color="silver", k="Not your own case",
             s="re-attest, and wait"),
    ], button=("Set the mark", "brand")),
    # 180: talking to a stranger. First card is the defect and it is the
    # whole round — the routes took no credential at all — and the last is
    # the one that needed none: a scan is somebody with no account.
    dict(num=180, title="Two Strangers", sub="An id is not a credential",
         accent="indigo", tab=27, cards=[
        dict(icon="mask", color="red", k="Not who you name",
             s="the token says who asks",
             pill=("401", "warn")),
        dict(icon="eye", color="indigo", k="An alias, and no more",
             s="never a name, never an id"),
        dict(icon="shield", color="amber", k="Held back stays back",
             s="only the sender sees it"),
        dict(icon="link", color="green", k="A scan needs nothing",
             s="they have no account yet"),
    ], button=("Find somebody", "brand")),
    # 179: the visitor's side of a desk. First card is the defect — a 401
    # that still left a room behind it — and the third is the sentence the
    # whole desk feature rests on, inverted from the mark.
    dict(num=179, title="Ringing The Bell", sub="The other side of the counter",
         accent="cyan", tab=26, cards=[
        dict(icon="lock", color="red", k="No trace, if refused",
             s="a refusal writes nothing",
             pill=("401", "warn")),
        dict(icon="bell", color="cyan", k="Ring without an account",
             s="the visitor has none yet"),
        dict(icon="eye", color="green", k="Live person, not AI",
             s="the mark, the other way up"),
        dict(icon="finger", color="amber", k="Ask, do not enter",
             s="coming up is the host's call"),
    ], button=("Ring the bell", "brand")),
    # 178: signing. The first card is the defect — a package missing a field
    # came back saying the signature was invalid, which is the worst thing
    # this endpoint can say and it was not true — and the third is the reason
    # the ceremony is a window rather than a request.
    dict(num=178, title="Signed, And Checked", sub="A missing field is not a forgery",
         accent="gold", tab=25, cards=[
        dict(icon="shield", color="red", k="Unrun is not failed",
             s="nor is it a pass",
             pill=("8", "warn")),
        dict(icon="pen", color="gold", k="Over these bytes",
             s="the challenge is the document"),
        dict(icon="finger", color="brand", k="Its own window",
             s="a token in a URL lands in logs"),
        dict(icon="eye", color="green", k="Checks on its own",
             s="the maths, not our word"),
    ], button=("Open the ceremony", "brand")),
    # 177: the other end of a delegation policy. The round with no defect in
    # it, so no card carries a fix — the first is the rule that makes the
    # feature what it is, and the third is the thing the offer deliberately
    # will not tell you.
    dict(num=177, title="Work Handed Over", sub="To somebody else's profile",
         accent="indigo", tab=24, cards=[
        dict(icon="link", color="indigo", k="Talk to it first",
             s="not a stranger with an id",
             pill=("403", "warn")),
        dict(icon="finger", color="brand", k="Hand it a job",
             s="not one more chat turn"),
        dict(icon="lock", color="amber", k="Scope stays theirs",
             s="you are told which phases"),
        dict(icon="eye", color="green", k="Both may watch it",
             s="the owner, and you"),
    ], button=("Hand it over", "brand")),
    dict(num=176, title="A Body, And What It Learns", sub="Listed, and not yet buyable",
         accent="silver", tab=23, cards=[
        dict(icon="clock", color="silver", k="Shown, not sold",
             s="listed so you see it coming",
             pill=("409", "warn")),
        dict(icon="coin", color="brand", k="On sale now",
             s="or an order book is open"),
        dict(icon="brain", color="green", k="Taught a verb",
             s="each task becomes a command"),
        dict(icon="shield", color="amber", k="Only what it can do",
             s="a vacuum is never taught fetch"),
    ], button=("Fit it", "brand")),
    # 175: inside a room. The first card is the defect that mattered most —
    # the speaker was read out of the body, so a room id was enough to talk
    # as somebody else — and the last is the microphone's whole point.
    dict(num=175, title="Inside A Room", sub="Knowing the id is not being here",
         accent="cyan", tab=22, cards=[
        dict(icon="mask", color="red", k="Not who you say",
             s="the token names the speaker",
             pill=("403", "warn")),
        dict(icon="eye", color="cyan", k="Read by the room",
             s="an id rides on a sticker"),
        dict(icon="brain", color="green", k="Every turn is marked",
             s="synthetic, as it is said"),
        dict(icon="bell", color="amber", k="A lent ear is shown",
             s="to everyone here, always"),
    ], button=("Say it", "brand")),
    # 174: the seller's side. The first card is the defect the screen was
    # built to make visible — two currencies that had been added together —
    # and the last is the door that asked for no credential at all.
    dict(num=174, title="What You Are Owed", sub="One currency at a time",
         accent="gold", tab=21, cards=[
        dict(icon="coin", color="gold", k="Not added together",
             s="a total across two is not one",
             pill=("2", "warn")),
        dict(icon="pen", color="brand", k="Post what it costs",
             s="and stop offering it later"),
        dict(icon="eye", color="green", k="Who holds one",
             s="and what they made from it"),
        dict(icon="lock", color="amber", k="Only a claimant",
             s="may take a listing down"),
    ], button=("Request a payout", "brand")),
    # 173: beginning and passing on. The card that matters is the second —
    # the one route an owner token cannot open, because the signal it
    # answers is that the owner cannot act.
    dict(num=173, title="Beginning, And Passing On", sub="The owner cannot authorise this",
         accent="silver", tab=20, cards=[
        dict(icon="dove", color="silver", k="A reviewer, not you",
             s="the owner may be gone",
             pill=("403", "warn")),
        dict(icon="lock", color="amber", k="Frozen, not orphaned",
             s="when nobody was named"),
        dict(icon="pen", color="green", k="It names itself",
             s="from what you said of them"),
        dict(icon="coin", color="brand", k="Sales follow the token",
             s="never a name in the body"),
    ], button=("Pass it on", "brand")),
    # 172: one named thing. The inversion is the point — the campaign is
    # the most public read in the product, and that is what makes it honest.
    dict(num=172, title="One Thing, Named", sub="Six reads, six answers",
         accent="gold", tab=19, cards=[
        dict(icon="eye", color="gold", k="A campaign: open",
             s="so its split can be seen",
             pill=("OPEN", "info")),
        dict(icon="coin", color="amber", k="Say where it goes",
             s="before asking anyone for it"),
        dict(icon="mask", color="green", k="What was taken out",
             s="counted, before it left"),
        dict(icon="lock", color="brand", k="Yours, not the room's",
             s="and the note says which"),
    ], button=("Look it up", "brand")),
    # 171: what leaves. Two different kinds of leaving, and the two facts
    # that shaped the screen: the preview is a dry run, and the adult bar
    # moved from delivery to the till.
    dict(num=171, title="What Leaves, And On What Terms", sub="Two kinds of leaving",
         accent="cyan", tab=18, cards=[
        dict(icon="eye", color="cyan", k="A dry run",
             s="what would leave, not what is",
             pill=("SIM", "warn")),
        dict(icon="mask", color="green", k="Names taken out",
             s="and a ref to delete it by"),
        dict(icon="coin", color="amber", k="Refused at the till",
             s="never after the fee moved"),
        dict(icon="rotate", color="brand", k="Take it back",
             s="stops, and asks for deletion"),
    ], button=("Stop, and take it back", "brand")),
    # 170: reaching out. The four refusals, and the point that only two of
    # them belong to the owner. The quiet-hours card is the one that took a
    # decision — it is the recipient's, and the owner is refused it.
    dict(num=170, title="Reaching Out, And What Stops It", sub="Four refusals, two of them yours",
         accent="indigo", tab=17, cards=[
        dict(icon="clock", color="indigo", k="Quiet hours",
             s="theirs to set, not yours",
             pill=("403", "warn")),
        dict(icon="bell", color="amber", k="Awaiting a reply",
             s="never twice into silence"),
        dict(icon="finger", color="cyan", k="A rating is theirs",
             s="and it can send an exchange"),
        dict(icon="brain", color="green", k="What it learned",
             s="shown, so it can be argued with"),
    ], button=("Reach out now", "brand")),
    # 169: the codes. Two pictures that look identical and go opposite ways,
    # and the fact that made the whole screen: there is no way to check a
    # code without adding to the number you are checking.
    dict(num=169, title="Where People Find You", sub="Two codes, opposite directions",
         accent="cyan", tab=16, cards=[
        dict(icon="qr", color="cyan", k="A placed code",
             s="brings them here to you"),
        dict(icon="link", color="amber", k="A platform code",
             s="sends them somewhere else"),
        dict(icon="eye", color="green", k="Looking is free",
             s="opening it counts as a scan",
             pill=("COUNTS", "warn")),
        dict(icon="shield", color="brand", k="Collect never posts",
             s="two rows, never one"),
    ], button=("Show its code", "brand")),
    dict(num=168, title="Who Follows, And What They Pay", sub="Nothing bills on a timer",
         accent="amber", tab=15, cards=[
        dict(icon="coin", color="amber", k="A period is a press",
             s="never a schedule, ever",
             pill=("SIM", "warn")),
        dict(icon="finger", color="cyan", k="The price you agreed",
             s="sent back to confirm it"),
        dict(icon="person", color="green", k="Verified age to gift",
             s="unverified is not evidence"),
        dict(icon="shield", color="brand", k="Who gets credited",
             s="read from the profile, not you"),
    ], button=("Charge another period", "brand")),
    # 167: the lobby. The whole design is one sentence, and the cards are
    # the three ways somebody would try to get around it — a machine of its
    # own, a second pad, a capture card — plus the instruction the synthetic
    # member is actually given, which is the only checkable part.
    dict(num=167, title="In The Game With You", sub="Observes and talks; never plays",
         accent="green", tab=15, cards=[
        dict(icon="people", color="green", k="Who is synthetic",
             s="said per member, not in a note",
             pill=("OPEN", "good")),
        dict(icon="finger", color="red", k="No input, ever",
             s="not one key, stick or click"),
        dict(icon="shield", color="amber", k="Not with more hardware",
             s="a second pad is the same bot"),
        dict(icon="doc", color="cyan", k="What it is told",
             s="that the others are synthetic too"),
    ], button=("Open the lobby", "brand")),
    # 166: the referral. Every card is a place where the design chose the
    # more awkward option — a separate read-it-first step, a signature over
    # the bytes rather than a tick, a link that dies on first use, and the
    # sentence that the thing you were talking to is not a clinician.
    dict(num=166, title="Somebody Qualified", sub="Once, and only with your signature",
         accent="red", tab=15, cards=[
        dict(icon="warn", color="red", k="Not a clinician",
             s="and the summary says so first",
             pill=("AI", "crit")),
        dict(icon="doc", color="cyan", k="Read it, then sign",
             s="nothing has gone anywhere yet"),
        dict(icon="finger", color="brand", k="Over these exact words",
             s="the challenge is their hash"),
        dict(icon="lock", color="amber", k="The link works once",
             s="a second try says when"),
    ], button=("Sign it with your device", "brand")),
    # 165: what it can do for you. The last card is the pair of answers a
    # provenance check gives, which can disagree — a real credential and
    # altered content — and reporting only the first would be the one
    # failure a mark must not have.
    dict(num=165, title="What It Can Do For You", sub="And the mark on what it makes",
         accent="brand", tab=15, cards=[
        dict(icon="list", color="brand", k="Sort a pile",
             s="with the reason each survived",
             pill=("RANKED", "info")),
        dict(icon="pen", color="cyan", k="Fix a draft",
             s="the rewrite and the reasons"),
        dict(icon="watch", color="green", k="Only what you wear",
             s="a room mic is refused, with why"),
        dict(icon="shieldok", color="amber", k="Two questions, not one",
             s="issued here, and unaltered"),
    ], button=("Check this mark", "brand")),
    # 164: the workshop. The first card is the material and the sentence
    # that follows from it — material in the clear is readable, and the
    # screen shows the words rather than a tick. The last card is the pair
    # of writes that used to accept a wrong key and answer 200.
    dict(num=164, title="What It Is Made Of", sub="Material, manner, and who it asks",
         accent="green", tab=15, cards=[
        dict(icon="doc", color="green", k="What it knows",
             s="shown, because it is readable",
             pill=("OPEN", "warn")),
        dict(icon="sliders", color="brand", k="How it comes across",
             s="manner, never permissions"),
        dict(icon="people", color="cyan", k="Who it hands work to",
             s="a domain, and who knows more"),
        dict(icon="shieldok", color="amber", k="A wrong key now refuses",
             s="it used to answer 200"),
    ], button=("Fold it back in", "brand")),
    # 163: a body. The middle two cards are the pair that is easy to get
    # wrong from the route names alone — what the body accepts is one list,
    # what it was told is another — and the last is the limit that matters
    # to whoever is standing next to it.
    dict(num=163, title="A Body To Speak Through", sub="Same person, new form",
         accent="cyan", tab=15, cards=[
        dict(icon="robot", color="cyan", k="The same person",
             s="identity holds across bodies",
             pill=("BOUND", "good")),
        dict(icon="finger", color="brand", k="What it accepts",
             s="this model, plus what it learned"),
        dict(icon="list", color="amber", k="Everything it was told",
             s="a body keeps a record"),
        dict(icon="shield", color="green", k="Steering is manner",
             s="never what it may be told"),
    ], button=("Tell it to tidy", "brand")),
    # 162: rated placement. Every card is a place the age wall does *not*
    # move to, which is the only reason the feature is defensible. The
    # third card is the one people get wrong: taking a placement down kills
    # the code already printed at the venue rather than repointing it.
    dict(num=162, title="Where It Is Marketed", sub="The wall does not travel",
         accent="red", tab=15, cards=[
        dict(icon="lock", color="red", k="Wherever found",
             s="the 18+ wall still resolves here",
             pill=("18+", "crit")),
        dict(icon="grid", color="cyan", k="A link or a printed code",
             s="the venue carries one or both"),
        dict(icon="rotate", color="amber", k="Take it down and it dies",
             s="the printed code stops resolving"),
        dict(icon="chart", color="green", k="Counts, never people",
             s="who scanned is never recorded"),
    ], button=("Place it", "brand")),
    # 161: a refusal, drawn. This is not a tab — it is the card that appears
    # inside whichever screen was refused. It is drawn because the backend
    # builds this refusal as an object for a screen to read, and for a while
    # the console flattened it into text; a picture of what the object is for
    # is the clearest way to keep it from happening again. The price and the
    # simulated-billing note sit on the same card on purpose.
    dict(num=161, title="Not On This Plan", sub="What was wanted, and what it costs",
         accent="amber", tab=15, cards=[
        dict(icon="lock", color="amber", k="Named, not barred",
             s="the refusal says which capability",
             pill=("PRO", "warn")),
        dict(icon="coin", color="brand", k="$130 a month",
             s="simulated — no real funds move"),
        dict(icon="person", color="cyan", k="You are on free",
             s="so you can see the distance"),
        dict(icon="doc", color="green", k="Nothing is lost",
             s="what you typed is still there"),
    ], button=("See the plans", "brand")),
    dict(num=160, title="Show Me Around", sub="The tour, and the pane",
         accent="cyan", tab=15, cards=[
        dict(icon="compass", color="cyan", k="Written steps",
             s="the same tour every time",
             pill=("STEP 1", "info")),
        dict(icon="doc", color="brand", k="What am I looking at",
             s="every screen has a lesson"),
        dict(icon="grid", color="amber", k="The pane that follows",
             s="it shows, it never acts"),
        dict(icon="mask", color="green", k="No name, no face",
             s="so it is furniture, not a 35th"),
    ], button=("Start the tour", "brand")),
    dict(num=159, title="Contest A Profile", sub="Restricted before review",
         accent="red", tab=15, cards=[
        dict(icon="flag", color="red", k="Restricted at once",
             s="before anyone reviews it",
             pill=("HELD", "crit")),
        dict(icon="rotate", color="green", k="Dismissal restores it",
             s="back to exactly what it was"),
        dict(icon="person", color="cyan", k="No account needed",
             s="a proof reference, not a login"),
        dict(icon="lock", color="brand", k="Every step recorded",
             s="sealed where a vault exists"),
    ], button=("Withdraw my consent", "brand")),
    dict(num=158, title="What Is Live", sub="And what the room is told",
         accent="amber", tab=15, cards=[
        dict(icon="eye", color="amber", k="Your camera is on",
             s="and your screen shows it",
             pill=("LIVE", "warn")),
        dict(icon="lock", color="brand", k="They cannot zoom",
             s="the holder points the phone"),
        dict(icon="mic", color="cyan", k="Only what you wear",
             s="near-field, never the room"),
        dict(icon="mask", color="green", k="A person underneath",
             s="every wearer is named"),
    ], button=("Stop sharing", "brand")),
    dict(num=157, title="Where It Is Seen", sub="Your page, and other people's walls",
         accent="cyan", tab=15, cards=[
        dict(icon="pen", color="brand", k="The page you make",
             s="your own HTML, mostly"),
        dict(icon="grid", color="cyan", k="Lobby panel",
             s="read by passers-by",
             pill=("LIVE", "good")),
        dict(icon="lock", color="amber", k="Never messages",
             s="an audience they never chose"),
        dict(icon="eye", color="green", k="What it shows is public",
             s="the list of screens is not"),
    ], button=("Place it on a screen", "brand")),
    dict(num=156, title="Who This Is", sub="One badge, and it moves",
         accent="brand", tab=15, cards=[
        dict(icon="person", color="brand", k="Four profiles",
             s="any of them anonymous"),
        dict(icon="shieldok", color="green", k="One verified",
             s="the badge moves, not renews",
             pill=("HERE", "good")),
        dict(icon="mask", color="cyan", k="Your writing is not",
             s="hidden — only what we publish"),
        dict(icon="warn", color="amber", k="Delete itemises",
             s="one count per record kind"),
    ], button=("Move the badge here", "brand")),
    # (Watch faces 10 and 11 mirror these two — docs/watch/build.py.)
    # A posted video is not a live desk. There is nobody at a desk to ring
    # and no host to ask, so the strip is only the three verbs that mean
    # something here — a control that cannot do anything is worse than absent.
    dict(num=100, title="Video Full Screen", full=True, accent="cyan",
         facade=dict(platform="YouTube", title="the compounding talk",
                     note="nothing is requested until you press play"),
         live_bar=[("heart", "pink"), ("chat", "brand"), ("share", "cyan")]),
    dict(num=101, title="Video Held", full=True, accent="cyan",
         facade=dict(platform="YouTube", title="the compounding talk",
                     note="nothing is requested until you press play"),
         held=[("?", None, "brandA", "Help"),
               (None, "rotate", "cyan", "Landscape"),
               (None, "shrink", "t2", "Back to app")],
         live_bar=[("heart", "pink"), ("chat", "brand"), ("share", "cyan")]),
    dict(num=102, title="Video Landscape", full=True, landscape=True,
         accent="cyan",
         facade=dict(platform="YouTube", title="the compounding talk",
                     note="nothing is requested until you press play"),
         live_bar=[("heart", "pink"), ("chat", "brand"), ("share", "cyan")]),
    # The rooms that are not a camera pointed at a desk. A room's channel can
    # be chat, voice, video, AR or VR (`POST /rooms`), and each of them gets
    # the same three states — plain full screen, held, and turned sideways —
    # because those are states of a *room*, not features of one screen.
    #
    # Audio first, because it is the case every layout forgets. There is
    # nothing to look at, so the boxes are the screen.
    dict(num=103, title="Audio Room", full=True, accent="green",
         voices=[
             ("Marcus Bell", frames.PORTRAITS[1][1], "speaking", "AI"),
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], "listening", "AI"),
             ("David Bianchi", frames.FOUNDER_VERIFIED[1], "listening", None),
             ("Priya Raman", frames.PORTRAITS[2][1], "muted", "AI"),
             ("Elena Duarte", frames.PORTRAITS[3][1], "listening", "AI"),
             ("Jonathan Reyes", frames.PORTRAITS[4][1], "muted", "AI"),
         ],
         live_bar=[("mic", "amber"), ("comeup", "green"), ("heart", "pink"),
                   ("share", "cyan")]),
    dict(num=104, title="Audio Held", full=True, accent="green",
         voices=[
             ("Marcus Bell", frames.PORTRAITS[1][1], "speaking", "AI"),
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], "listening", "AI"),
             ("David Bianchi", frames.FOUNDER_VERIFIED[1], "listening", None),
             ("Priya Raman", frames.PORTRAITS[2][1], "muted", "AI"),
             ("Elena Duarte", frames.PORTRAITS[3][1], "listening", "AI"),
             ("Jonathan Reyes", frames.PORTRAITS[4][1], "muted", "AI"),
         ],
         held=[("?", None, "brandA", "Help"),
               (None, "rotate", "cyan", "Landscape"),
               (None, "shrink", "t2", "Back to app")],
         live_bar=[("mic", "amber"), ("comeup", "green"), ("heart", "pink"),
                   ("share", "cyan")]),
    dict(num=105, title="Audio Landscape", full=True, landscape=True,
         accent="green", voices=[
             ("Marcus Bell", frames.PORTRAITS[1][1], "speaking", "AI"),
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], "listening", "AI"),
             ("David Bianchi", frames.FOUNDER_VERIFIED[1], "listening", None),
             ("Priya Raman", frames.PORTRAITS[2][1], "muted", "AI"),
             ("Elena Duarte", frames.PORTRAITS[3][1], "listening", "AI"),
             ("Jonathan Reyes", frames.PORTRAITS[4][1], "muted", "AI"),
         ],
         live_bar=[("mic", "amber"), ("comeup", "green"), ("heart", "pink"),
                   ("share", "cyan")]),
    # AR: the room is the one you are already in, with the others placed in
    # it. The camera frame is real and carries no AI mark; the people standing
    # in it are synthetic and carry theirs — which is the single place a
    # missing badge would matter most.
    dict(num=106, title="AR Room", full=True, accent="cyan",
         photo=frames.DESK, photo_tag=("AR", "sample"),
         ar_presence=[
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], 0.26, 0.46, 1.0),
             ("Marcus Bell", frames.PORTRAITS[1][1], 0.72, 0.38, 0.82),
         ],
         live_bar=[("mic", "amber"), ("comeup", "green"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    dict(num=107, title="AR Held", full=True, accent="cyan",
         photo=frames.DESK, photo_tag=("AR", "sample"),
         ar_presence=[
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], 0.26, 0.46, 1.0),
             ("Marcus Bell", frames.PORTRAITS[1][1], 0.72, 0.38, 0.82),
         ],
         held=[("?", None, "brandA", "Help"),
               (None, "rotate", "cyan", "Landscape"),
               (None, "shrink", "t2", "Back to app")],
         live_bar=[("mic", "amber"), ("comeup", "green"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    dict(num=108, title="AR Landscape", full=True, landscape=True,
         accent="cyan", photo=frames.DESK, photo_tag=("AR", "sample"),
         ar_presence=[
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], 0.20, 0.52, 1.0),
             ("Marcus Bell", frames.PORTRAITS[1][1], 0.50, 0.40, 0.86),
             ("Priya Raman", frames.PORTRAITS[2][1], 0.78, 0.48, 0.94),
         ],
         # No chat overlay here. The presence markers already name everyone in
         # the room, and a bubble repeating "Dr. Amara Osei" under her own
         # label is the same name twice with a collision between them.
         live_bar=[("mic", "amber"), ("comeup", "green"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    # VR: a room that is not a place. Drawn rather than photographed, because
    # there is no photograph of somewhere that does not exist, and a stock
    # picture of a headset would be a picture of the hardware instead of the
    # room. Depth is carried by size and position — which is the whole of what
    # 3-D buys over a grid of boxes.
    dict(num=109, title="VR Room", full=True, accent="brand",
         space=dict(label="VR · 3-D", avatars=[
             ("Marcus Bell", frames.PORTRAITS[1][1], 0.22),
             ("David Bianchi", frames.FOUNDER_VERIFIED[1], 0.55),
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], 0.86),
         ]),
         live_bar=[("mic", "amber"), ("comeup", "green"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    dict(num=110, title="VR Held", full=True, accent="brand",
         space=dict(label="VR · 3-D", avatars=[
             ("Marcus Bell", frames.PORTRAITS[1][1], 0.22),
             ("David Bianchi", frames.FOUNDER_VERIFIED[1], 0.55),
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], 0.86),
         ]),
         held=[("?", None, "brandA", "Help"),
               (None, "rotate", "cyan", "Landscape"),
               (None, "shrink", "t2", "Back to app")],
         live_bar=[("mic", "amber"), ("comeup", "green"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    dict(num=111, title="VR Landscape", full=True, landscape=True,
         accent="brand",
         space=dict(label="VR · 3-D", avatars=[
             ("Marcus Bell", frames.PORTRAITS[1][1], 0.18),
             ("Priya Raman", frames.PORTRAITS[2][1], 0.42),
             ("David Bianchi", frames.FOUNDER_VERIFIED[1], 0.64),
             ("Dr. Amara Osei", frames.PORTRAITS[0][1], 0.88),
         ]),
         live_bar=[("mic", "amber"), ("comeup", "green"), ("gift", "gold"),
                   ("heart", "pink"), ("share", "cyan")]),
    # The agreement window. Two people about to send each other work, and the
    # document they both sign before anything moves — see `qrme/exchange.py`.
    # The manifest is the screen: what crosses, which way, and how big, because
    # "what am I about to receive" should be a list rather than an assurance.
    dict(num=112, title="The Agreement", sub="Before anything moves",
         accent="gold", tab=0, cards=[
        dict(icon="doc", color="gold", k="Checkout flow",
             s="software · agreed by both", pill=("DRAFT", "warn")),
        dict(icon="link", color="cyan", k="spec.pdf → them",
             s="document · 240 KB"),
        dict(icon="bolt", color="amber", k="checkout.zip → you",
             s="source · 1.4 MB · runs", pill=("RUNS", "crit")),
        dict(icon="shieldok", color="green", k="Included when done",
             s="the source · a handover call"),
        dict(icon="cross", color="red", k="Not included",
             s="hosting · ongoing support"),
    ], button=("Sign — 1 of 2", "brand")),
    # The rule the whole design turns on, given its own screen because it is
    # the one people will not believe until they see it happen.
    dict(num=113, title="Signatures Cleared", sub="The manifest changed",
         accent="red", tab=0, cards=[
        dict(icon="warn", color="red", k="An item was added",
             s="both signatures dropped", pill=("VOID", "crit")),
        dict(icon="person", color="amber", k="You signed", s="at 14:02 — cleared"),
        dict(icon="person", color="amber", k="They signed", s="at 14:03 — cleared"),
        dict(icon="lock", color="cyan", k="Nothing moved",
             s="the channel never opened"),
        dict(icon="doc", color="green", k="Read it again",
             s="then both sign the new one"),
    ], button=("Review the manifest", "brand")),
    # Delivery: a signed agreement makes items available, it does not place
    # them. Each one is taken separately by the side receiving it.
    dict(num=114, title="Delivery", sub="Nothing arrives on its own",
         accent="green", tab=0, cards=[
        dict(icon="shieldok", color="green", k="Both signed",
             s="channel open · 2 items", pill=("OPEN", "good")),
        dict(icon="doc", color="cyan", k="spec.pdf", s="accepted 14:11",
             pill=("TAKEN", "good")),
        dict(icon="bolt", color="amber", k="checkout.zip",
             s="source · waiting for you", pill=("ACCEPT", "warn")),
        dict(icon="warn", color="red", k="It runs on your machine",
             s="signing is not a code review"),
        dict(icon="lock", color="brand", k="No device access",
             s="the listed items, and nothing else"),
    ], button=("Accept checkout.zip", "amber")),
    # The watch party, in the app. A posted video, the people and the profiles
    # in the room, and the line that keeps the embed promise.
    dict(num=115, title="Watch Party", sub="Together, on your own play button",
         accent="cyan", tab=0,
         facade_card=dict(platform="YouTube", title="the compounding talk",
                          note="the room shares a position, not a player"),
         cards=[
        dict(icon="people", color="cyan", k="4 people · 2 profiles",
             s="each marked for what it is"),
        dict(icon="finger", color="amber", k="The host holds it",
             s="the position — everyone follows"),
        dict(icon="shieldok", color="green", k="Profiles have not seen it",
             s="told so, not just starved"),
    ], button=("Join the party", "brand")),
    # Lending a skill inside a place two people already share. The card that
    # matters is the last one: either of them can end it, alone.
    dict(num=116, title="Lend a Skill", sub="Both agree · either can stop",
         accent="cyan", tab=0, cards=[
        dict(icon="db", color="amber", k="Finance Pack",
             s="offered into this room", pill=("OFFER", "warn")),
        dict(icon="people", color="cyan", k="Marcus → you",
             s="use it here, while you both want"),
        dict(icon="lock", color="green", k="Nothing is copied",
             s="no install, no licence, no copy"),
        dict(icon="eye", color="brand", k="He sees every use",
             s="which is why it is worth lending"),
        dict(icon="cross", color="red", k="Either of you can stop it",
             s="alone, with no agreement needed"),
    ], button=("Accept the loan", "brand")),
    # Editing what you already said. The screen exists because the feature is
    # invisible otherwise: the interesting part is not the edit box, it is what
    # happens to the answer that was written under the old wording.
    dict(num=117, title="Edit a Message", sub="The correction carries forward",
         accent="brand", tab=0, cards=[
        dict(icon="pen", color="brand", k="“Born in 1985.”",
             s="edited — it said 1885", pill=("EDITED", "info")),
        dict(icon="chat", color="amber", k="Answered the old",
             s="written before your edit", pill=("STALE", "warn")),
        dict(icon="shieldok", color="green", k="Re-moderated on edit",
             s="not a way past the filter"),
        dict(icon="eye", color="cyan", k="The next turn reads 1985",
             s="history is rebuilt every turn"),
        dict(icon="doc", color="red", k="Retract keeps the row",
             s="text stops counting, trail stays"),
    ]),
    # Anonymity, and the card that keeps it honest is the fourth one. A screen
    # that listed only what is withheld would be read as a promise of
    # untraceability, and somebody deciding whether it is safe to post would
    # decide on the strength of it.
    dict(num=118, title="Stay Anonymous", sub="What we withhold, and what we can't",
         accent="cyan", tab=3, cards=[
        dict(icon="mask", color="brand", k="Anonymous 41338025",
             s="tied to this profile, not you"),
        dict(icon="lock", color="pink", k="You cannot change it",
             s="so nobody can pick a real name"),
        dict(icon="lock", color="cyan", k="Your account is hidden",
             s="your profiles cannot be matched"),
        dict(icon="addphoto", color="cyan", k="Your own picture",
             s="or a field emblem, or neither"),
        dict(icon="warn", color="amber", k="Your writing is still yours",
             s="people who know you may tell"),
    ], button=("Turn it off", "amber")),
    # Several profiles and one badge, on one screen — because the rule only
    # makes sense next to the thing it constrains. Three rows, one verified,
    # one anonymous, one invented, which is the whole vocabulary.
    dict(num=119, title="Your Profiles", sub="As many as you like · one verified",
         accent="brand", tab=3, cards=[
        dict(icon="person", color="green", k="Work · verified",
             s="a real person — you, checked", pill=("BADGE", "good")),
        # You see your own name here. Everybody else gets the subtitle.
        dict(icon="mask", color="cyan", k="Weekend self",
             s="shown as anonymous persona", pill=("HIDDEN", "info")),
        dict(icon="robot", color="indigo", k="Captain Nobody",
             s="invented — nobody to verify"),
        # Both of these said the rule instead of saying what it does for you.
        # "One badge, not three" only counts if you count the rows above it,
        # and "it says you are one person" parses as the badge making a claim
        # about your personhood. "One at a time, not one forever" is the
        # argument in `qrme/identity.py` compressed into a riddle — fine in a
        # docstring, where the reader came looking for the reasoning; useless
        # on a card, where they came to find a control.
        dict(icon="shieldok", color="brand", k="Only one can be verified",
             s="the badge means this is you"),
        dict(icon="rotate", color="amber", k="Move it to another",
             s="yours to move, any time"),
    ], button=("Move the badge", "brand")),
    # Channel 2 off the room. The last two cards are the ones that make the
    # list a rule rather than an inventory: every place here has other people
    # in it who can be shown the disclosure, which is the test a surface has
    # to pass to be on the screen at all.
    dict(num=120, title="Lend It Anywhere", sub="The same microphone, other places",
         accent="cyan", tab=3, cards=[
        dict(icon="people", color="brand", k="In a watch party",
             s="the others watching hear you", pill=("LENT", "good")),
        dict(icon="speaker", color="cyan", k="On a live desk",
             s="your visitors, while it is open"),
        dict(icon="chat", color="indigo", k="In a 1:1 connection",
             s="the other person, and no one else"),
        dict(icon="eye", color="green", k="Everyone here is told",
             s="and can be shown the disclosure"),
        dict(icon="shieldok", color="amber", k="Ends when it does",
             s="it cannot outlive the place"),
    ], button=("Take it back", "amber")),
    # Wearing a character over your own camera. The last two cards are the
    # feature: an overlay is synthetic media on a real face, so the screen that
    # offers it is also the screen that says what it can never be.
    dict(num=121, title="Wear a Character", sub="Seventeen faces, and your own",
         accent="pink", tab=3, cards=[
        dict(icon="mask", color="pink", k="Blue Fox",
             s="driven by your own expressions", pill=("WORN", "good")),
        dict(icon="photo", color="cyan", k="Your background only",
             s="your face is untouched"),
        dict(icon="eye", color="green", k="Everyone here is told",
             s="they see the name, not a face"),
        dict(icon="warn", color="red", k="Never a real person",
             s="no likeness of anybody real"),
        dict(icon="shieldok", color="green", k="Live person — not AI",
             s="the badge stays, mask and all"),
    ], button=("Take it off", "amber")),
    # The lobby. Every row says what it is — that is the screen's whole job,
    # and it is why the human row is drawn identically to the synthetic ones
    # except for the word: a roster that styled people differently would be
    # telling you by decoration what it should be telling you in text.
    dict(num=122, title="Game Lobby", sub="Who is in the match, and what they are",
         accent="indigo", tab=3, cards=[
        dict(icon="robot", color="indigo", k="Vex · your teammate",
             s="the session profile, hosting", pill=("AI", "info")),
        dict(icon="robot", color="cyan", k="Rook · coach",
             s="your second profile, watching", pill=("AI", "info")),
        dict(icon="bolt", color="amber", k="Your spotter",
             s="an agent — needs you", pill=("AMBER", "warn")),
        dict(icon="person", color="green", k="samhain · a person",
             s="the only human on the roster", pill=("YOU", "good")),
        dict(icon="shieldok", color="brand", k="Nothing here plays",
             s="they observe and talk, that is all"),
    ], button=("Seat another", "brand")),
    # The desk badge with a mask on it. The screen exists because the pair is
    # the disclosure: either line alone is a different and wrong claim, so the
    # first two cards are deliberately adjacent and equally weighted.
    dict(num=123, title="Masked and Real", sub="One mark, whatever you wear",
         accent="green", tab=3, cards=[
        dict(icon="shieldok", color="green", k="NOT AI · REAL PERSON",
             s="burned in — mask or none"),
        dict(icon="person", color="cyan", k="@otis_marsh",
             s="top left, where it always was"),
        dict(icon="lock", color="indigo", k="Tied to your account",
             s="no one else can paste it on"),
        dict(icon="eye", color="brand", k="They know whose room",
             s="they chose it to get here"),
        dict(icon="mask", color="pink", k="Change your face too",
             s="see Wear a Character"),
    ], button=("Change the mask", "brand")),
    # Backgrounds, and the third card is the whole reason this is not just a
    # picker: a generated room is synthetic media even when the face is not.
    dict(num=124, title="Your Background", sub="Yours, imported, or generated",
         accent="cyan", tab=3, cards=[
        dict(icon="photo", color="cyan", k="Your kitchen",
             s="your own photo, no mark needed", pill=("ON", "good")),
        dict(icon="link", color="indigo", k="Imported image",
             s="you need the rights to it"),
        dict(icon="brain", color="pink", k="A generated scene",
             s="AI-made — and it says so", pill=("AI", "info")),
        dict(icon="eye", color="brand", k="Blur your real room",
             s="the room you are really in"),
        dict(icon="mask", color="green", k="Change your face too",
             s="see Wear a Character"),
    ], button=("Change background", "brand")),
    # The hardware answer to the fair-play rule, refused on its own screen
    # because it is the workaround somebody will actually propose.
    dict(num=125, title="Never a Player", sub="Synthetic members sit beside you",
         accent="red", tab=3, cards=[
        dict(icon="warn", color="red", k="Never a player slot",
             s="not on your console either"),
        dict(icon="cross", color="red", k="No second controller",
             s="the same bot, shorter cable"),
        dict(icon="cross", color="pink", k="No Bluetooth pad",
             s="pairing one is the tell"),
        dict(icon="cross", color="amber", k="No capture card",
             s="watching to play is playing"),
        dict(icon="people", color="green", k="Beside the players",
             s="coach, spotter, archivist"),
    ]),
    # A profile on a fixture. The third and fourth cards are why this is not
    # just the watch again: a wrist is read by its owner and a wall by whoever
    # walks past, so the list of what may be shown is shorter, not longer.
    dict(num=126, title="On a Screen", sub="A wall, a kiosk, a pane of glass",
         accent="cyan", tab=3, cards=[
        dict(icon="grid", color="cyan", k="The lobby panel",
             s="wall, kiosk, counter, window", pill=("LIVE", "good")),
        dict(icon="expand", color="brand", k="Full, half, or a strip",
             s="and opaque or see-through"),
        dict(icon="eye", color="amber", k="Only what strangers read",
             s="a wall cannot tell who is there"),
        dict(icon="warn", color="red", k="No control on a wall",
             s="pressed by whoever reaches it"),
        dict(icon="shieldok", color="green", k="The mark gets a plate",
             s="on glass it must stay legible"),
    ], button=("Take it down", "amber")),
    # The guided walkthrough. The third card is the one that keeps it honest:
    # the guide has no name and no face, which on a platform full of disclosed
    # synthetic people is the difference between furniture and a character.
    dict(num=127, title="Show Me Around", sub="The guide, not a profile",
         accent="brand", tab=3, cards=[
        dict(icon="compass", color="brand", k="Seven chapters",
             s="sixteen steps, in order", pill=("STEP 1", "info")),
        dict(icon="speaker", color="cyan", k="Read it or hear it",
             s="voice drops the numbers"),
        dict(icon="mask", color="amber", k="No name, no face",
             s="it is furniture, not somebody"),
        dict(icon="lock", color="green", k="It never taps for you",
             s="it tells you what to tap"),
        dict(icon="shieldok", color="indigo", k="Every screen covered",
             s="a test holds it to the app"),
    ], button=("Start the tour", "brand")),
    # The pane in the corner. Card four is the one that decides the design: a
    # dock is inside every screenshot and every screen share, so it tucks
    # itself away on a surface that is going out, and it never carries a
    # control that could be mis-tapped onto a live broadcast.
    dict(num=128, title="The Corner Pane", sub="Tucks away with the helper",
         accent="brand", tab=3, cards=[
        dict(icon="shrink", color="brand", k="Tap to tuck it away",
             s="the helper button is the handle"),
        dict(icon="watch", color="cyan", k="The watch faces, here",
             s="no watch required"),
        dict(icon="warn", color="amber", k="It shows, it never acts",
             s="the real screen is one tap away"),
        dict(icon="eye", color="red", k="It is in your screenshot",
             s="so it tucks itself on a live"),
        dict(icon="compass", color="green", k="Every face has a way out",
             s="it points at the screen"),
    ], button=("Move it left", "brand")),
    # Directions rather than a description. The second card is the whole
    # point: somebody asking where a thing is has not asked what it is.
    dict(num=129, title="Where Is It?", sub="Ask, and the guide points",
         accent="cyan", tab=3, cards=[
        dict(icon="search", color="brand", k="Change my background",
             s="Your Background · screen 124"),
        dict(icon="compass", color="cyan", k="It names the screen",
             s="not a paragraph about it"),
        dict(icon="shrink", color="indigo", k="And the corner pane",
             s="when the face is in there too"),
        dict(icon="speaker", color="green", k="Say it or type it",
             s="the same answer either way"),
        dict(icon="lock", color="amber", k="It still never taps",
             s="it tells you where to"),
    ], button=("Ask the guide", "brand")),
    # The price list. Card five is the one that has to be there: money in this
    # repository is simulated everywhere, and a tier screen is the one place a
    # reader would assume otherwise.
    dict(num=130, title="Choose a Plan", sub="Free builds too — $20 seals it",
         accent="brand", tab=3, cards=[
        dict(icon="eye", color="amber", k="Free · $0",
             s="the same app, in the clear", pill=("NOW", "info")),
        dict(icon="lock", color="cyan", k="Basic · $20/month",
             s="the same app, sealed in a vault"),
        dict(icon="bolt", color="brand", k="Pro · $130/month",
             s="all that leaves your account"),
        dict(icon="person", color="green", k="Free does all Basic does",
             s="$20 buys privacy, not features"),
        dict(icon="info", color="indigo", k="Billing is simulated",
             s="no real funds move", pill=("SIM", "warn")),
    ], button=("Go Pro", "brand")),
    # What Basic cannot reach, said plainly rather than by a greyed-out row
    # with no explanation. The last card is the design: browsing stays open.
    dict(num=131, title="What Pro Adds", sub="The things that leave your account",
         accent="cyan", tab=3, cards=[
        dict(icon="grid", color="cyan", k="The marketplace",
             s="list, sell, license, place"),
        dict(icon="link", color="indigo", k="Connectors and apps",
             s="reach outside services"),
        dict(icon="share", color="green", k="Lend and borrow skills",
             s="plus standing connections"),
        dict(icon="sliders", color="brand", k="Builders and modifiers",
             s="steering, governance, more"),
        dict(icon="search", color="amber", k="Browsing stays open",
             s="look before you pay"),
    ], button=("Compare plans", "brand")),
    # ---- first-run: the plan step ----
    #
    # Distinct from 130, which is the reference price list reached from
    # settings. This is the one in the signup flow, and the difference that
    # matters is the third card: you can decline and keep looking, because a
    # visitor is a real state rather than a lapsed customer.
    dict(num=132, title="Pick a Plan", sub="Step 4 of 5",
         accent="brand", tab=0, cards=[
        dict(icon="eye", color="amber", k="Free · $0",
             s="make things — stored in the clear"),
        dict(icon="lock", color="cyan", k="Basic · $20/month",
             s="the same, sealed in a vault"),
        dict(icon="bolt", color="brand", k="Pro · $130/month",
             s="all that leaves your account"),
        dict(icon="shieldok", color="green", k="Change or cancel later",
             s="your profiles outlive the plan"),
        dict(icon="info", color="indigo", k="Billing is simulated",
             s="no real funds move", pill=("SIM", "warn")),
    ], button=("Start free", "brand")),
    # The payment step, marked. Drawn rather than skipped because a signup
    # flow has one and pretending otherwise would make the mockups a worse
    # guide than the product — but every version of this screen carries the
    # simulation pill, because a convincing checkout is the one place in this
    # repository somebody could reasonably be misled about money.
    dict(num=133, title="Payment", sub="Step 5 of 5",
         accent="cyan", tab=0, cards=[
        dict(icon="coin", color="amber", k="Basic · $20 a month",
             s="first charge today", pill=("SIM", "warn")),
        dict(icon="lock", color="green", k="Card details",
             s="nothing is sent anywhere"),
        dict(icon="warn", color="red", k="No processor is called",
             s="the subscription is a row"),
        dict(icon="cal", color="cyan", k="Renews monthly",
             s="cancel from settings"),
        dict(icon="shieldok", color="indigo", k="Leave and keep it all",
             s="cancelling deletes nothing"),
    ], button=("Confirm — simulated", "brand")),
    # Where signup lands. The fourth card is the honest half of an upsell:
    # naming what is not included beats discovering it at a wall.
    dict(num=134, title="You're on Basic", sub="Here is what that means",
         accent="green", tab=0, cards=[
        dict(icon="shieldok", color="green", k="Make what you like",
             s="profiles, and your own agent", pill=("ON", "good")),
        dict(icon="lock", color="cyan", k="Sealed in the vault",
             s="that is what the $20 bought"),
        dict(icon="grid", color="amber", k="Marketplace is Pro",
             s="you can browse it now"),
        dict(icon="link", color="amber", k="Connectors are Pro",
             s="so are lent skills"),
        dict(icon="sliders", color="amber", k="Builders are Pro",
             s="steering and governance"),
        dict(icon="compass", color="brand", k="The guide knows the way",
             s="ask it where anything is"),
    ], button=("Start building", "brand")),
    # The 402 moment, in context. This is what the structured refusal is for:
    # a client shows a price rather than a permission error.
    dict(num=135, title="This Needs Pro", sub="What you tapped, and why",
         accent="amber", tab=3, cards=[
        dict(icon="lock", color="amber", k="Listing on the market",
             s="needs Pro · $130/month"),
        dict(icon="person", color="cyan", k="You are on Basic",
             s="nothing changes on its own"),
        dict(icon="search", color="green", k="Keep browsing free",
             s="looking was never gated"),
        dict(icon="bolt", color="brand", k="What else Pro adds",
             s="connectors, skills, builders"),
        dict(icon="info", color="indigo", k="Billing is simulated",
             s="no real funds move", pill=("SIM", "warn")),
    ], button=("Upgrade to Pro", "brand")),
    # Channel 3. Card one is the whole pitch — describing a knocking engine is
    # the hard part; pointing at it is trivial.
    dict(num=136, title="Show Them", sub="Channel 3 · point, don't describe",
         accent="cyan", tab=3, cards=[
        dict(icon="eye", color="cyan", k="Point at the engine",
             s="a mechanic watches, live"),
        dict(icon="clock", color="brand", k="Runs for 15 minutes",
             s="45 is the ceiling"),
        dict(icon="finger", color="green", k="You point it, always",
             s="no zoom, no torch, no shutter"),
        dict(icon="eye", color="amber", k="Nothing is kept",
             s="recording is a separate yes"),
        dict(icon="warn", color="red", k="Ends with the room",
             s="or the moment you say stop"),
    ], button=("Start sharing", "brand")),
    # The rule that decides everything. Card two is the inversion: the subject
    # governs, not the audience.
    dict(num=137, title="What's In Shot", sub="The subject sets the rules",
         accent="brand", tab=3, cards=[
        dict(icon="gear", color="green", k="A thing · anyone",
             s="engine, boiler, board, leak"),
        dict(icon="doc", color="cyan", k="A document · anyone",
             s="it carries names and numbers"),
        dict(icon="grid", color="amber", k="A place · anyone",
             s="whoever is there is in shot"),
        dict(icon="person", color="red", k="A body · a person only",
             s="never a synthetic profile"),
        dict(icon="warn", color="indigo", k="We cannot see the room",
             s="look before you start"),
    ]),
    # ---- the free plan ----
    #
    # Where signup lands now. The order of the cards is the argument: what is
    # *not* private is said before anything about what the plan can do,
    # because a disclosure that arrives after the pitch is a disclosure nobody
    # reads at the moment it matters.
    dict(num=138, title="You're on Free", sub="The same app, in the clear",
         accent="amber", tab=0, cards=[
        dict(icon="eye", color="red", k="Not private",
             s="no vault, no key, no audit trail", pill=("OPEN", "warn")),
        dict(icon="person", color="green", k="All that Basic does",
             s="profiles, and your own agent", pill=("ON", "good")),
        dict(icon="lock", color="cyan", k="$20 buys privacy",
             s="not one extra feature"),
        dict(icon="warn", color="amber", k="Some things we refuse",
             s="see what free will not hold"),
        dict(icon="info", color="indigo", k="Billing is simulated",
             s="no real funds move", pill=("SIM", "warn")),
    ], button=("Seal it for $20", "brand")),
    # The two postures side by side. The last two cards are the ones a pricing
    # page normally leaves out, and leaving them out is how a product ends up
    # selling absolution rather than encryption.
    dict(num=139, title="Where It Lives", sub="Who holds it, and how",
         accent="cyan", tab=3, cards=[
        dict(icon="grid", color="amber", k="Free · we hold it",
             s="we host it, you have access"),
        dict(icon="eye", color="red", k="Operators can read it",
             s="so can a lawful request"),
        dict(icon="lock", color="green", k="Basic · you hold it",
             s="sealed to you, not to us"),
        dict(icon="shieldok", color="cyan", k="Upgrading seals ahead",
             s="it cannot un-expose the past"),
        dict(icon="shield", color="indigo", k="A lapse unseals nothing",
             s="a lapse is not a disclosure"),
    ], button=("Move to Basic", "brand")),
    # What the open store will not hold, and the test for the list: whose
    # exposure is it. Both entries are somebody who never chose the plan.
    dict(num=140, title="Not On Free", sub="What we will not leave open",
         accent="red", tab=3, cards=[
        dict(icon="person", color="red", k="Somebody else's letters",
             s="they did not pick this plan"),
        dict(icon="doc", color="red", k="A clinician's note",
             s="the patient did not pick it"),
        dict(icon="eye", color="amber", k="Behind the age gate",
             s="rated work needs the vault"),
        dict(icon="shieldok", color="green", k="Your own work is fine",
             s="your notes, your call"),
        dict(icon="lock", color="cyan", k="Basic · $20 a month",
             s="the vault is free to host"),
    ], button=("Seal it for $20", "brand")),
    dict(num=88, title="Your Devices", sub="Pair them while you sign up",
         accent="cyan", tab=0, cards=[
        dict(icon="watch", color="cyan", k="Apple Watch", s="on the wrist · agents, activity", pill=("PAIRED", "good")),
        dict(icon="mic", color="green", k="AirPods", s="in the ears", pill=("PAIRED", "good")),
        dict(icon="mic", color="indigo", k="Lapel mic", s="clipped to the collar"),
        dict(icon="eye", color="amber", k="Glasses · ring · pendant", s="worn on the person"),
        dict(icon="shield", color="red", k="Smart speakers refused", s="they hear whoever walks in"),
    ], button=("Pair a device", "brand")),
    dict(num=87, title="For You", sub="And why each one is here",
         accent="cyan", tab=0, cards=[
        dict(icon="person", color="green", k="Marcus Bell", s="a friend posted this", pill=("110", "good")),
        dict(icon="person", color="cyan", k="Dr. Amara Osei", s="you have talked to this profile", pill=("70", "good")),
        dict(icon="chart", color="amber", k="Priya Raman", s="you engage with technology", pill=("35", "warn")),
        dict(icon="eye", color="indigo", k="Wren Okafor", s="popular with people here", pill=("28", "info")),
        dict(icon="shield", color="red", k="Never ranked on", s="memories · source items · vault"),
    ]),
    dict(num=86, title="Customise", sub="Themes, colour, your Top 8",
         accent="amber", tab=0, cards=[
        dict(icon="sparkle", color="amber", k="Theme", s="Sunset · six presets", pill=("PICKED", "good")),
        dict(icon="eye", color="indigo", k="Accent colour", s="#f7b731 — validated, not markup"),
        dict(icon="chat", color="cyan", k="Tagline", s="90 characters, in your words"),
        dict(icon="person", color="green", k="Top 8", s="friends only, your order"),
        # Raw HTML *is* allowed — that is the MySpace part, and refusing it
        # would have been refusing the feature. What is not allowed is script.
        dict(icon="pen", color="indigo", k="Your own HTML", s="marquee, tables, backgrounds"),
        dict(icon="shield", color="red", k="Script is stripped", s="the nostalgia, not the injection"),
    ], button=("Save page", "brand")),
]


# Characters that must not reach a filename, because the filename becomes a URL
# in the README's <img src>. A "?" starts a query string and a "#" a fragment,
# so `129-where-is-it?.svg` silently resolves to `129-where-is-it` and the image
# is a broken icon. A comma survives the URL but not every shell.
#
# One function rather than the expression written out twice, which is how a
# comma reached a filename once already: the copy that swept away stale files
# and the copy that wrote new ones disagreed, so the build both created the bad
# name and declined to clean it up.
_UNSAFE = str.maketrans({c: None for c in "?#,:!'\"()[]{}<>|\\^`*$&+;@="})


def slug(title: str) -> str:
    """The filename part of a screen's title, safe to put in a URL."""
    out = (title.lower().replace(" & ", "-").replace(" ", "-")
                .replace("\u00e9", "e").translate(_UNSAFE))
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def filename(screen: dict) -> str:
    """The one place a screen's file is named."""
    return f'{screen["num"]:02d}-{slug(screen["title"])}.svg'


def main():
    global PLATFORM
    total = 0
    # Renaming a screen used to leave the old file behind, and a stale SVG on
    # disk is worse than a missing one: it still renders, it is still linked,
    # and it shows a version of the product that no longer exists. Renumbering
    # the room screens left six of them lying there before this was noticed.
    stale = 0
    for plat, sub in (("ios", ""), ("android", "android")):
        PLATFORM = plat
        outdir = OUT if not sub else os.path.join(OUT, sub)
        os.makedirs(outdir, exist_ok=True)
        keep = {filename(s) for s in SCREENS}
        for name in os.listdir(outdir):
            if name.endswith(".svg") and name not in keep:
                os.remove(os.path.join(outdir, name))
                stale += 1
        for s in SCREENS:
            n = s["num"]
            fn = filename(s)
            draw = render_full if s.get("full") else render
            # Rendered before the file is opened. `open(..., "w")` truncates
            # immediately, so doing it the other way round meant a render that
            # raised left a zero-byte SVG behind — a build that fails by
            # corrupting its own output, and the empty file then crashed the
            # audit rather than being reported by it.
            svg = draw(s)
            with open(os.path.join(outdir, fn), "w") as f:
                f.write(svg)
            total += 1
    PLATFORM = "ios"
    print(f"generated {total} screens ({total // 2} × 2 platforms)"
          + (f", removed {stale} stale" if stale else ""))
    return []


if __name__ == "__main__":
    main()
