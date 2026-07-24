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


def button(x, y, w, label, kind="brand", h=42):
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


def head(num, title, sub, accent="brand", locked=False):
    ac = ACCENT.get(accent, C["brandA"])
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)} screen">']
    out.append(f'''<defs>
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
    </defs>''')
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
def card_block(y, c):
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
def render(spec):
    num = spec["num"]
    out = head(f"{num:02d}", spec["title"], spec.get("sub", ""),
               spec.get("accent", "brand"), spec.get("locked", False))
    y = SY + 100
    hero = spec.get("hero")

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
        out.append(text(CX + 18, y + 10, "Stored locally in your vault · optional cloud contribution", 9.3, C["t3"], 500))

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
        out.append(orb(cx0, y + 42, 34))
        out.append(icon("person", cx0, y + 40, "rgba(255,255,255,0.92)", 1.5))
        out.append(f'<circle cx="{cx0}" cy="{y+42}" r="40" fill="none" stroke="url(#gBrand)" stroke-width="2.5"/>')
        out.append(text(cx0, y + 98, "Ava", 21, "#fff", 750, "middle"))
        out.append(text(cx0, y + 116, "AI Version Me", 11.5, C["t2"], 500, "middle"))
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
        out.append(button(CX, y, CW, "Chat with Ava", "brand", 42))
        out.append(button(CX, y + 50, (CW - 10) / 2, "Customize", "ghost", 38))
        out.append(button(CX + (CW - 10) / 2 + 10, y + 50, (CW - 10) / 2, "View Memory", "ghost", 38))

    elif hero == "chat":
        out.append(f'<circle cx="{CX+13}" cy="{y+11}" r="13" fill="url(#orb)"/>')
        out.append(text(CX + 32, y + 8, "Ava", 12, C["txt"], 650))
        out.append(f'<circle cx="{CX+52}" cy="{y+5}" r="2.5" fill="{C["green"]}"/>')
        out.append(text(CX + 58, y + 8, "Online", 9.5, C["green"], 600))
        y += 24
        # AI bubble
        out.append(rrect(CX, y, CW - 40, 66, 14, "url(#gCard)", C["line"], 1))
        for i, ln in enumerate(["Hey David, I noticed you haven't", "checked in this week.",
                                 "Want to talk about the garden? 🌱"]):
            out.append(text(CX + 14, y + 22 + i * 15, ln, 11, C["txt"], 400))
        y += 78
        # user bubble
        out.append(rrect(CX + 60, y, CW - 60, 40, 14, "url(#gBrand)"))
        out.append(text(CX + CW - 14, y + 17, "Hey Ava! I've been busy,", 10.5, "#fff", 500, "end"))
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
        qs = [("1", "What do you love most?", "answered"),
              ("2", "What's a memory you'd keep forever?", "answered"),
              ("3", "How do you comfort a friend?", "now"),
              ("4", "What would you never compromise on?", "next")]
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
        out.append(text(W / 2, y, "@ava.bianchi", 14, C["brandA"], 700, "middle"))
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
        for ic, col, k, s in [("eye", "cyan", "Anonymized at the gateway", "no ids, names replaced"),
                              ("warn", "red", "Revoke deletes past items", "erased by their refs")]:
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
                                  ("sliders", "green", "Inference & fine-tune", "recomputed on-host", ("LOCAL", "good")),
                                  ("eye", "cyan", "GET /offline/status", "proves the posture", ("PROVEN", "info"))]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "pill": pt, "h": 48})
            out.append(s2)

    elif hero == "memorial":
        out.append(orb(W / 2, y + 38, 30))
        out.append(icon("dove", W / 2, y + 38, "rgba(255,255,255,0.95)", 1.6))
        y += 82
        out.append(text(W / 2, y, "Ava", 20, "#fff", 750, "middle"))
        out.append(text(W / 2, y + 18, "@ava.bianchi · a memorial", 10.5, C["t2"], 500, "middle"))
        y += 40
        for ic, col, k, s in [("dove", "cyan", "Graceful departure", "a farewell for every relationship"),
                              ("lock", "green", "Memory preserved", "sealed in the vault, exportable"),
                              ("people", "amber", "Succession", "ownership passes, old token revoked"),
                              ("chat", "brand", "Chat closes with 410", "a goodbye, never a silent 404")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)

    elif hero == "moderation":
        out.append(rrect(CX, y, CW, 64, 16, "url(#gCard)", C["line"], 1))
        out.append(icon("chat", CX + 22, y + 22, C["brandA"], 0.8))
        out.append(text(CX + 40, y + 20, "Ava wants to reply", 11, C["t2"], 600))
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
        for ic, col, k, s in [("chat", "brand", "Talked with Ava", "12 messages this session"),
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
        out.append(text(CX, y, "A 2D portrait for chat, a 3D avatar for video, AR & VR.", 10.5, C["t2"]))
        y += 26
        gw = (CW - 12) / 2
        # 2D portrait tile
        out.append(rrect(CX, y, gw, 128, 16, "url(#gCard)", C["line"], 1))
        out.append(orb(CX + gw / 2, y + 54, 30))
        out.append(icon("person", CX + gw / 2, y + 52, "rgba(255,255,255,0.92)", 1.4))
        out.append(pill(CX + gw - 12, y + 20, "2D", "brand"))
        out.append(text(CX + gw / 2, y + 104, "Portrait", 11.5, C["txt"], 650, "middle"))
        out.append(text(CX + gw / 2, y + 118, "chat & feed", 9.5, C["t2"], 400, "middle"))
        # 3D avatar tile
        gx = CX + gw + 12
        out.append(rrect(gx, y, gw, 128, 16, "url(#gCard)", C["line"], 1))
        out.append(ring(gx + gw / 2, y + 54, 30, 0.75, C["cyan"], 4))
        out.append(orb(gx + gw / 2, y + 54, 24))
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
        for ic, col, k, s in [("headset", "cyan", "Room-scale presence", "Ava stands in your space"),
                              ("speaker", "brand", "Spatial audio", "her voice comes from where she is"),
                              ("eye", "pink", "Passthrough AR or full VR", "your living room, or her world")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)

    elif hero == "video":
        vh = 196
        out.append(rrect(CX, y, CW, vh, 18, "url(#orb)", C["line"], 1))
        out.append(rrect(CX, y, CW, vh, 18, "url(#glow)"))
        out.append(orb(W / 2, y + vh / 2 - 12, 44))
        out.append(icon("person", W / 2, y + vh / 2 - 14, "rgba(255,255,255,0.95)", 1.9))
        # LIVE badge
        out.append(rrect(CX + 14, y + 14, 58, 20, 10, A(C["red"], 0.9)))
        out.append(f'<circle cx="{CX+26}" cy="{y+24}" r="3.5" fill="#fff"/>')
        out.append(text(CX + 34, y + 28, "LIVE", 10.5, "#fff", 750))
        out.append(text(CX + 14, y + vh - 26, "Ava", 13, "#fff", 700))
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
        out.append(text(W / 2, y, "Camera & mic stay on your device — the stream is encrypted.", 9.3, C["t3"], 500, "middle"))

    elif hero == "allset":
        out.append(orb(W / 2, y + 40, 34))
        out.append(f'<path d="M{W/2-11} {y+40} l7 8 14 -16" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
        y += 100
        out.append(text(W / 2, y, "You're all set", 18, "#fff", 750, "middle", -0.3))
        out.append(text(W / 2, y + 21, "Ava is ready to meet the world.", 11, C["t2"], 400, "middle"))
        y += 44
        for ic, col, k, s in [("person", "brand", "Profile created", "Ava · AI version of you"),
                              ("db", "cyan", "Sources added", "1,024 memories sealed in your vault"),
                              ("sliders", "amber", "Personality set", "warm · balanced boundaries"),
                              ("mask", "pink", "Avatar ready", "2D portrait + 3D for video & VR")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)
        out.append(button(CX, y + 2, CW, "Start chatting with Ava", "brand", 44))

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
        out.append(text(CX, y, "Only the folders & albums you pick — nothing else is read.",
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
        for c in spec["cards"]:
            s, y = card_block(y, c)
            out.append(s)
        if spec.get("button"):
            out.append(button(CX, y, CW, spec["button"][0], spec["button"][1], 42))

    out += tabbar(spec.get("tabs", MAIN), spec.get("tab", 0))
    out += navbar()
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
    dict(num=6, title="Chat with Ava", sub="Every response explained", hero="chat", accent="brand", tab=0),
    dict(num=7, title="Memory Vault", sub="Your AI remembers", hero="vault", accent="cyan", tabs=VAULT, tab=0, locked=True),
    dict(num=8, title="Relationships", sub="People in Ava's life", hero="relationships", accent="amber", tabs=REL, tab=0),
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
        dict(icon="chat", color="pink", k="“How did the garden do?”", s="only if you set proactive scope", pill=("SCOPED", "brand")),
        dict(icon="clock", color="cyan", k="Quiet hours honored", s="22:00 – 07:00 · rate-capped 24h"),
        dict(icon="shieldok", color="green", k="Moderated & anti-spam", s="no repeat until you reply"),
    ], button=("Reply", "brand")),
    dict(num=19, title="Transparency", sub="Honest about multiplicity", accent="brand", tab=0, cards=[
        dict(icon="people", color="brand", k="12 active relationships", s="acknowledged truthfully if asked", pill=("OPEN", "brand")),
        dict(icon="eye", color="cyan", k="GET /transparency", s="who it talks to, disclosed by design"),
        dict(icon="chat", color="amber", k="“Yes, I know others too.”", s="every prompt instructs honesty"),
    ]),
    dict(num=20, title="Connections", sub="Meet other real people", accent="pink", tab=0, tabs=MARKET, cards=[
        dict(icon="people", color="pink", k="Friendly tier", s="matched anonymously by alias", pill=("OPEN", "good")),
        dict(icon="shield", color="red", k="Rated tier · 18+", s="age-verified both ends"),
        dict(icon="warn", color="amber", k="Per-tier moderation", s="minors always strict · blocks never sent"),
    ]),
    dict(num=21, title="Rooms", sub="Chat, voice, video, AR, VR", accent="cyan", tab=0, cards=[
        dict(icon="chat", color="brand", k="Multiparty conversation", s="users + profiles, any mix"),
        dict(icon="people", color="cyan", k="profile ↔ profile", s="they advance on their own"),
        dict(icon="headset", color="pink", k="Any channel", s="chat · voice · video · AR · VR"),
        dict(icon="shieldok", color="green", k="A minor present → strict", s="every profile turn moderated"),
    ]),
    dict(num=22, title="Providers", sub="When AI hands off to a human", accent="cyan", tab=0, tabs=MARKET, cards=[
        dict(icon="cross", color="red", k="Bay Area Wellness", s="mental health · 0.8 mi", pill=("OPEN", "good")),
        dict(icon="chart", color="green", k="Certified Financial Planner", s="finance · telehealth"),
        dict(icon="link", color="cyan", k="Consented handoff", s="session sealed in the vault, revocable"),
    ]),
    # ---- data promise & lifecycle ----
    dict(num=23, title="Cloud Model", sub="Greater model, opt-in", hero="cloud", accent="brand", tabs=CONTROL, tab=0),
    dict(num=24, title="Offline Mode", sub="A hard guarantee", hero="offline", accent="green", tabs=CONTROL, tab=0),
    dict(num=25, title="Objection & Lifecycle", sub="A real person can contest", hero="objection", accent="amber", tab=0),
    dict(num=26, title="Memorial", sub="Graceful departure", hero="memorial", accent="cyan", tab=0),
    # ---- assistant & claims 21–26 ----
    dict(num=27, title="AI Assistant", sub="A capable creative partner", accent="brand", tab=0, cards=[
        dict(icon="list", color="brand", k="Triage & curate", s="keep the best N, auditable score"),
        dict(icon="pen", color="amber", k="Proofread in your voice", s="improved draft + edit suggestions"),
        dict(icon="eye", color="cyan", k="Perceive the scene", s="hands-free, step-by-step guidance"),
        dict(icon="star2", color="pink", k="Compose a work", s="music, poem, note — kept as an artifact"),
    ]),
    dict(num=28, title="Specialists", sub="Biometric-routed handoff", accent="cyan", tab=0, cards=[
        dict(icon="heart", color="red", k="Stress detected", s="HR +38 · from JIM-mini", extra=("spark", [60, 68, 80, 95, 108], "red")),
        dict(icon="brain", color="pink", k="Handed off", s="mental-health agent, this turn", pill=("ENGAGED", "brand")),
        dict(icon="link", color="cyan", k="Sustained across turns", s="until a reading shows recovery"),
        dict(icon="person", color="green", k="Then hands back", s="profile speaks again", pill=("RETURNED", "good")),
    ]),
    dict(num=29, title="Tasks & Grants", sub="Autonomous, revocable", accent="amber", tab=0, cards=[
        dict(icon="gift", color="amber", k="Scoped grant issued", s="a revocable vault token", pill=("SCOPED", "brand")),
        dict(icon="list", color="brand", k="research → draft → send", s="one phase at a time"),
        dict(icon="clock", color="cyan", k="Pauses at confirm", s="resumes in a later session"),
        dict(icon="warn", color="red", k="Revoke halts the next read", s="raw data never retained"),
    ]),
    dict(num=30, title="Fine-Tune", sub="Encrypted, offline (Claim 26)", accent="green", tab=2, cards=[
        dict(icon="sliders", color="green", k="Recompute embeddings", s="all local · no external calls", pill=("LOCAL", "good")),
        dict(icon="lock", color="cyan", k="Sealed in the vault", s="adaptation artifact encrypted"),
        dict(icon="chart", color="brand", k="Run recorded", s="metrics · external_transmission: false"),
    ], button=("Run Fine-Tune", "brand")),
    dict(num=31, title="Your Data Promise", sub="No raw data leaves your vault", accent="green", tabs=CONTROL, tab=0, cards=[
        dict(icon="lock", color="green", k="Sealed at rest", s="AES-256-GCM · tenant-isolated", pill=("VAULT", "good")),
        dict(icon="eye", color="cyan", k="Every access audited", s="stored · read · erased", pill=("CHAIN OK", "good")),
        dict(icon="finger", color="brand", k="Capability tokens", s="only the SHA-256 hash is stored"),
        dict(icon="warn", color="red", k="Delete anything, anytime", s="local trace + vault records purged"),
    ]),
    # ---- moderation, posting & the persona engine ----
    dict(num=32, title="Moderation", sub="Every reply, before it's seen", hero="moderation", accent="green", tab=0),
    dict(num=33, title="Posts", sub="Post in your AI's voice", accent="amber", tabs=MARKET, tab=3, cards=[
        dict(icon="pen", color="amber", k="Compose a post", s="in Ava's voice, then moderated"),
        dict(icon="chat", color="brand", k="“Tomatoes are in — finally.”", s="posted to the feed", pill=("LIVE", "good")),
        dict(icon="shieldok", color="green", k="Public posts → strict", s="always the strict filter"),
        dict(icon="chart", color="cyan", k="12 posts · 3.4k views", s="GET /posts"),
    ]),
    dict(num=34, title="Adult Mode", sub="Age-gated at both ends", accent="red", tab=0, locked=True, cards=[
        dict(icon="lock", color="red", k="Adult content mode", s="an adult owner must enable it", pill=("18+", "crit")),
        dict(icon="finger", color="green", k="Owner verified 18+", s="required to turn it on", stat=("VERIFIED", "on")),
        dict(icon="person", color="amber", k="Interactor 18+", s="verified before any chat", stat=("REQUIRED", "avail")),
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
        dict(icon="shield", color="amber", k="Command allowlist", s="Per-body limits · say is moderated"),
        dict(icon="list", color="pink", k="Command log", s="Every order audited"),
    ], button=("Bind a robot", "brand")),
    # ---- knowledge packs & robot task mods ----
    dict(num=57, title="Knowledge Packs", sub="Downloadable expertise, per industry", accent="amber", tabs=MARKET, tab=0, cards=[
        dict(icon="db", color="amber", k="Finance Field Pack", s="3 items · QRME Starter Collection", pill=("FREE", "good")),
        dict(icon="db", color="brand", k="Distributed Systems Pro", s="priced · explicit accept to buy", pill=("$29.99", "warn")),
        dict(icon="star2", color="green", k="Install → smarter", s="items join the source material"),
        dict(icon="eye", color="cyan", k="Provenance counts it", s="grounded_in.by_kind: pack"),
    ], button=("Download Field Pack", "brand")),
    dict(num=58, title="Robot Task Packs", sub="Task mods for the body it embodies", accent="cyan", tab=3, cards=[
        dict(icon="gear", color="cyan", k="Household Tasks Pack", s="sort_laundry · water_plants · set_table", pill=("FREE", "good")),
        dict(icon="shield", color="green", k="Capability-checked install", s="a vacuum is never sold manipulation"),
        dict(icon="lock", color="amber", k="Allowlist extended, not opened", s="unknown verbs still refused"),
        dict(icon="chart", color="pink", k="Every task audited", s="procedure carried in the result"),
    ], button=("Buy Culinary Assistant · 9.99", "brand")),
    dict(num=59, title="Embodied Agent", sub="The persona knows its body", accent="brand", tab=3, cards=[
        dict(icon="person", color="brand", k="Same identity in the body", s="never a second persona"),
        dict(icon="star2", color="cyan", k="Learned modules in the prompt", s="say knows what the body can do"),
        dict(icon="grid", color="green", k="Skills list", s="GET /robots/{id}/skills"),
        dict(icon="shieldok", color="amber", k="Revocable", s="uninstall revokes the verbs instantly"),
    ]),
    dict(num=60, title="Publish a Pack", sub="Your expertise, on the market", accent="amber", tabs=MARKET, tab=0, cards=[
        dict(icon="pen", color="amber", k="Bundle knowledge items", s="or task modules with requirements"),
        dict(icon="chart", color="brand", k="Free or priced", s="POST /packs · listed under #pack"),
        dict(icon="people", color="green", k="Installs tracked", s="catalog shows items · installs"),
    ], button=("Publish", "brand")),
    dict(num=61, title="Pack Registries", sub="Federated mod storefronts", accent="brand", tabs=MARKET, tab=0, cards=[
        dict(icon="building", color="brand", k="Robotmods.net", s="task mods for robot bodies", pill=("2 PACKS", "info")),
        dict(icon="building", color="cyan", k="LLMmods.com", s="knowledge mods for LLM personas", pill=("2 PACKS", "info")),
        dict(icon="shieldok", color="green", k="Origin on every label", s="publisher & storefront URL on the pack"),
        dict(icon="chart", color="amber", k="Same rules once synced", s="buy flow · capability checks · provenance"),
    ], button=("Sync sources", "brand")),
    dict(num=62, title="Rated Placement", sub="18+ marketing, walled at the source", accent="red", tabs=MARKET, tab=0, locked=True, cards=[
        dict(icon="building", color="red", k="Adult venues", s="OnlyFans · Fansly · x-rated directories", pill=("18+", "crit")),
        dict(icon="grid", color="amber", k="QR · @handle · #tag", s="publish the refs where adults are"),
        dict(icon="lock", color="green", k="The wall travels", s="every scan resolves through the age gate"),
        dict(icon="shieldok", color="cyan", k="Never another real person", s="self or fictional personas only"),
    ], button=("Place at a venue", "brand")),
    dict(num=63, title="Placement Analytics", sub="What each venue earns", accent="amber", tabs=MARKET, tab=0, locked=True, cards=[
        dict(icon="chart", color="amber", k="OnlyFans · 3 scans", s="2 walled · 1 verified", extra=("spark", [1, 1, 3, 2, 4], "amber")),
        dict(icon="chart", color="cyan", k="Fansly · 2 scans", s="0 walled · 2 verified"),
        dict(icon="people", color="green", k="Funnel", s="resolutions → verified → chatters", metric="25%"),
        dict(icon="shieldok", color="brand", k="Counted, never identified", s="owner-only · no viewer identities"),
    ]),
    dict(num=64, title="Creator Payouts", sub="One statement, every sale", accent="green", tabs=MARKET, tab=0, cards=[
        dict(icon="chart", color="green", k="Accrued balance", s="pack sales · license fees", metric="$86"),
        dict(icon="db", color="amber", k="Distributed Systems Pro", s="pack_sale · $29.99", pill=("ACCRUED", "warn")),
        dict(icon="pen", color="brand", k="consult license · Priya", s="license_fee · $49.00", pill=("PAID", "good")),
        dict(icon="shieldok", color="cyan", k="Written at sale time", s="a record, not a reconstruction"),
    ], button=("Request payout", "brand")),
    dict(num=65, title="Watch Remote", sub="Your agents, on your wrist", accent="green", tab=3, cards=[
        dict(icon="clock", color="green", k="ship the notes · working", s="phase: draft", pill=("GREEN", "good")),
        dict(icon="clock", color="amber", k="research brief · assist", s="awaiting: external confirmation", pill=("ORANGE", "warn")),
        dict(icon="clock", color="red", k="second job · stopped", s="cancelled from the wrist", pill=("RED", "crit")),
        dict(icon="person", color="brand", k="Kitchen NEO", s="quick ring: come here · patrol · dock · stop"),
        dict(icon="shieldok", color="cyan", k="No new powers, only reach", s="same auth · allowlists · moderation"),
    ], button=("Assist", "brand")),
    dict(num=67, title="Smart Glasses", sub="Capture the POV, render to the lens", accent="cyan", tab=3, cards=[
        dict(icon="eye", color="cyan", k="Ray-Ban Meta", s="capture · livestream · HUD caption", pill=("LINKED", "good")),
        dict(icon="eye", color="brand", k="Meta Ray-Ban Display", s="POV context · HUD overlay · nav"),
        dict(icon="compass", color="green", k="Google (Android XR)", s="Gemini POV · live-translation HUD"),
        dict(icon="photo", color="amber", k="Capture ⟷ render", s="collect the view in · produce to the lens"),
    ], button=("Connect glasses", "brand")),
    dict(num=68, title="Gaming Companion", sub="A teammate, synthetically operated", accent="indigo", tab=3, cards=[
        dict(icon="star2", color="indigo", k="Halo Infinite · Xbox", s="role: teammate · online multiplayer", pill=("LIVE", "good")),
        dict(icon="chat", color="brand", k="“Enemy on the flag — falling back, cover me”", s="in-character callout, moderated"),
        dict(icon="shieldok", color="green", k="Fair play, enforced", s="within the rules · never cheats"),
        dict(icon="people", color="cyan", k="Companion · teammate · practice", s="PlayStation · Xbox · Switch · Steam · PC"),
    ], button=("Start a session", "brand")),
    dict(num=66, title="Steering", sub="Tone, pace, age & appearance — one hub", accent="brand", tab=2, cards=[
        dict(icon="sliders", color="brand", k="Pace · Autonomy · Verbosity", s="throttle dials, 0–100"),
        dict(icon="sliders", color="amber", k="Warmth · Humor · Formality", s="behavior dials, 0–100"),
        dict(icon="person", color="cyan", k="Appearance", s="how it looks — rides on every surface"),
        dict(icon="clock", color="green", k="Age", s="base age · ages with time"),
        dict(icon="lock", color="red", k="Intimacy · 18+ only", s="adult-mode profiles · within boundaries", pill=("18+", "crit")),
        dict(icon="shieldok", color="green", k="Steering, not piloting", s="shapes presentation · never identity or safety"),
    ], button=("Apply", "brand")),
]


def main():
    global PLATFORM
    total = 0
    for plat, sub in (("ios", ""), ("android", "android")):
        PLATFORM = plat
        outdir = OUT if not sub else os.path.join(OUT, sub)
        os.makedirs(outdir, exist_ok=True)
        for s in SCREENS:
            n = s["num"]
            slug = s["title"].lower().replace(" & ", "-").replace(" ", "-").replace("é", "e")
            fn = f'{n:02d}-{slug}.svg'
            with open(os.path.join(outdir, fn), "w") as f:
                f.write(render(s))
            total += 1
    PLATFORM = "ios"
    print(f"generated {total} screens ({total // 2} × 2 platforms)")
    return []


if __name__ == "__main__":
    main()
