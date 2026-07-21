#!/usr/bin/env python3
"""Generate the QRME **desktop** app SVGs — wide, multi-panel dashboard views of
the QRME synthetic-profile platform, in the product's deep-indigo / neon-purple
design language. A sidebar-nav desktop window per view, complementing the mobile
app in docs/screens/.

Reuses the mobile generator's icon + colour library so both galleries stay one
system. Run: python3 docs/desktop/build.py  ->  docs/desktop/NN-name.svg
"""

from __future__ import annotations

import importlib.util
import os

OUT = os.path.dirname(os.path.abspath(__file__))

PLATFORM_D = "macos"          # "macos" | "windows"

_spec = importlib.util.spec_from_file_location(
    "qrmemobile", os.path.join(OUT, "..", "screens", "build.py"))
pb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pb)
icon, C, ACCENT, A = pb.icon, pb.C, pb.ACCENT, pb.A
rrect, text, pill, chip, button, ring, spark, esc, stars = (
    pb.rrect, pb.text, pb.pill, pb.chip, pb.button, pb.ring, pb.spark, pb.esc, pb.stars)

W, H = 1280, 820
WIN_X, WIN_Y, WIN_W, WIN_H = 24, 24, 1232, 772
TOPBAR_H = 54
SIDE_W = 216
CONTENT_X = WIN_X + SIDE_W
CONTENT_Y = WIN_Y + TOPBAR_H
CONTENT_W = WIN_W - SIDE_W
CONTENT_H = WIN_H - TOPBAR_H
PAD = 28
IX = CONTENT_X + PAD
IY = CONTENT_Y + PAD
IW = CONTENT_W - 2 * PAD

NAV = [("target", "Home"), ("chat", "Conversation"), ("people", "Relationships"),
       ("lock", "Memory"), ("compass", "Marketplace"), ("doc", "Licensing"),
       ("gear", "Control")]


def status_dot(x, y, label, tone):
    col = {"on": C["green"], "off": C["t3"], "avail": C["amber"], "crit": C["red"]}[tone]
    w = 14 + len(label) * 6.0
    return (rrect(x - w, y - 9, w, 16, 8, A(col, 0.14))
            + f'<circle cx="{x-w+9}" cy="{y-1}" r="3" fill="{col}"/>'
            + text(x - w + 16, y + 3, label, 9, col, 700, "start", 0.5))


def defs():
    return f'''<defs>
      <linearGradient id="gPage" x1="0" y1="0" x2="0.4" y2="1">
        <stop offset="0" stop-color="#0d0a20"/><stop offset="1" stop-color="#080614"/></linearGradient>
      <linearGradient id="gScr" x1="0" y1="0" x2="0.5" y2="1">
        <stop offset="0" stop-color="{C['scrA']}"/><stop offset="1" stop-color="{C['scrB']}"/></linearGradient>
      <linearGradient id="gSide" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#1b1445"/><stop offset="1" stop-color="#100b2c"/></linearGradient>
      <linearGradient id="gCard" x1="0" y1="0" x2="0.4" y2="1">
        <stop offset="0" stop-color="{C['card']}"/><stop offset="1" stop-color="{C['card2']}"/></linearGradient>
      <linearGradient id="gBrand" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="gAmber" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="{C['amber']}"/><stop offset="1" stop-color="#ffd27a"/></linearGradient>
      <radialGradient id="orb" cx="36%" cy="30%" r="78%">
        <stop offset="0" stop-color="#d9ccff"/><stop offset="38%" stop-color="{C['brandA']}"/>
        <stop offset="78%" stop-color="#3f3bc0"/><stop offset="100%" stop-color="#140f34"/></radialGradient>
    </defs>'''


def frame(title, active):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="QRME — {esc(title)}">']
    o.append(defs())
    o.append(rrect(0, 0, W, H, 0, "url(#gPage)"))
    o.append(f'<rect x="{WIN_X}" y="{WIN_Y}" width="{WIN_W}" height="{WIN_H}" rx="{10 if PLATFORM_D == "windows" else 18}" '
             f'fill="url(#gScr)" stroke="{C["line"]}" stroke-width="1"/>')
    o.append(rrect(WIN_X, WIN_Y, SIDE_W, WIN_H, 18, "url(#gSide)"))
    o.append(rrect(WIN_X + SIDE_W - 18, WIN_Y, 18, WIN_H, 0, "url(#gScr)"))
    o.append(f'<line x1="{CONTENT_X}" y1="{WIN_Y}" x2="{CONTENT_X}" y2="{WIN_Y+WIN_H}" stroke="{C["line"]}" stroke-width="1"/>')
    o.append(f'<line x1="{CONTENT_X}" y1="{CONTENT_Y}" x2="{WIN_X+WIN_W}" y2="{CONTENT_Y}" stroke="{C["line"]}" stroke-width="1"/>')
    if PLATFORM_D == "windows":
        _bx = WIN_X + WIN_W - 22
        o.append(f'<line x1="{_bx-70}" y1="{WIN_Y+28}" x2="{_bx-59}" y2="{WIN_Y+28}" stroke="{C["t2"]}" stroke-width="1.3"/>')
        o.append(rrect(_bx - 41, WIN_Y + 22, 11, 11, 1.5, "none", C["t2"], 1.3))
        o.append(f'<path d="M{_bx-11} {WIN_Y+22} l11 11 M{_bx} {WIN_Y+22} l-11 11" stroke="{C["t2"]}" stroke-width="1.3" stroke-linecap="round"/>')
    else:
        for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            o.append(f'<circle cx="{WIN_X+22+i*18}" cy="{WIN_Y+27}" r="5.5" fill="{col}" opacity="0.9"/>')
    o.append(f'<circle cx="{WIN_X+96}" cy="{WIN_Y+27}" r="11" fill="url(#orb)"/>')
    o.append(icon("person", WIN_X + 96, WIN_Y + 27, "rgba(255,255,255,0.95)", 0.6))
    o.append(text(WIN_X + 114, WIN_Y + 25, "QRME", 14, C["txt"], 800, spacing=0.5))
    o.append(text(WIN_X + 114, WIN_Y + 39, "Your identity. Your AI.", 8.5, C["t3"], 500))
    o.append(text(CONTENT_X + PAD, WIN_Y + 33, title, 15, C["txt"], 700, spacing=-0.2))
    rx = WIN_X + WIN_W - 24 - (86 if PLATFORM_D == 'windows' else 0)
    o.append(icon("gear", rx - 10, WIN_Y + 27, C["t2"], 0.8))
    o.append(status_dot(rx - 34, WIN_Y + 31, "Ava · Online", "on"))
    o.append(f'<circle cx="{rx-34-96}" cy="{WIN_Y+27}" r="13" fill="url(#orb)"/>')
    o.append(icon("person", rx - 34 - 96, WIN_Y + 27, "rgba(255,255,255,0.9)", 0.62))
    ny = CONTENT_Y + 18
    for ic, lbl in NAV:
        on = (lbl == active)
        if on:
            o.append(rrect(WIN_X + 12, ny - 4, SIDE_W - 24, 38, 10, A(C["brandA"], 0.16)))
            o.append(rrect(WIN_X + 12, ny - 4, 3, 38, 2, C["brandA"]))
        col = C["brandA"] if on else C["t2"]
        o.append(icon(ic, WIN_X + 34, ny + 15, col, 0.72))
        o.append(text(WIN_X + 54, ny + 20, lbl, 12.5, C["txt"] if on else C["t2"], 650 if on else 500))
        ny += 46
    o.append(f'<line x1="{WIN_X+16}" y1="{WIN_Y+WIN_H-70}" x2="{WIN_X+SIDE_W-16}" y2="{WIN_Y+WIN_H-70}" stroke="{C["line"]}" stroke-width="1"/>')
    o.append(rrect(WIN_X + 16, WIN_Y + WIN_H - 56, SIDE_W - 32, 40, 10, "rgba(255,255,255,0.04)", C["line"], 1))
    o.append(icon("lock", WIN_X + 34, WIN_Y + WIN_H - 36, C["green"], 0.66))
    o.append(text(WIN_X + 52, WIN_Y + WIN_H - 40, "Vault protected", 10.5, C["txt"], 650))
    o.append(text(WIN_X + 52, WIN_Y + WIN_H - 27, "AES-256-GCM · local", 8.5, C["t3"], 500))
    return o


def close():
    return ['</svg>']


def panel(x, y, w, h, title, right=None):
    o = [rrect(x, y, w, h, 14, "url(#gCard)", C["line"], 1)]
    if title:
        o.append(text(x + 18, y + 27, title, 12.5, C["txt"], 700))
    if right:
        o.append(text(x + w - 18, y + 27, right, 10, C["t3"], 600, "end"))
    return o


def tile(x, y, w, h, label, value, sub, col, ic, pillt=None):
    o = [rrect(x, y, w, h, 14, "url(#gCard)", C["line"], 1)]
    o.append(text(x + 18, y + 28, label, 11, C["t2"], 600))
    sz = 27 if len(value) <= 6 else 22
    o.append(text(x + 18, y + 62, value, sz, col, 800))
    o.append(text(x + 18, y + 80, sub, 9.5, C["t3"], 500))
    o.append(chip(x + w - 48, y + 14, ic, col))
    if pillt:
        o.append(pill(x + w - 16, y + h - 14, pillt[0], pillt[1]))
    return o


def areachart(x, y, w, h, pts, col):
    n = len(pts)
    lo, hi = min(pts), max(pts)
    pad = 0.12 * (hi - lo)
    lo -= pad
    rng = (hi - lo) or 1
    coords = [(x + w * i / (n - 1), y + h - (v - lo) / rng * h) for i, v in enumerate(pts)]
    line = " ".join(f"{a:.1f},{b:.1f}" for a, b in coords)
    o = []
    for gy in range(1, 4):
        yy = y + h * gy / 4
        o.append(f'<line x1="{x}" y1="{yy:.1f}" x2="{x+w}" y2="{yy:.1f}" stroke="{A(C["line"],0.5)}" stroke-width="1"/>')
    o.append(f'<polygon points="{x},{y+h} {line} {x+w},{y+h}" fill="{A(col,0.13)}"/>')
    o.append(f'<polyline points="{line}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    ex, ey = coords[-1]
    o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{col}"/>')
    return "".join(o)


def table(x, y, w, cols, rows, rowh=36):
    o = []
    cx = x
    for label, frac, align in cols:
        cw = w * frac
        ax = cx + 10 if align == "start" else (cx + cw - 10 if align == "end" else cx + cw / 2)
        o.append(text(ax, y + 12, label, 9.5, C["t3"], 700, align, 0.4))
        cx += cw
    o.append(f'<line x1="{x}" y1="{y+22}" x2="{x+w}" y2="{y+22}" stroke="{C["line"]}" stroke-width="1"/>')
    yy = y + 22
    for row in rows:
        cx = x
        for (label, frac, align), cell in zip(cols, row):
            cw = w * frac
            ax = cx + 10 if align == "start" else (cx + cw - 10 if align == "end" else cx + cw / 2)
            if isinstance(cell, tuple):
                txt, tcol, twt = cell
                o.append(text(ax, yy + 24, txt, 10.5, tcol, twt, align))
            else:
                o.append(text(ax, yy + 24, cell, 10.5, C["txt"], 500, align))
            cx += cw
        yy += rowh
        o.append(f'<line x1="{x}" y1="{yy}" x2="{x+w}" y2="{yy}" stroke="{A(C["line"],0.45)}" stroke-width="1"/>')
    return "".join(o)


# --------------------------------------------------------------------------- #
# views
# --------------------------------------------------------------------------- #
def v_home():
    o = []
    tw = (IW - 3 * 20) / 4
    tiles = [("Memory", "247", "entries", C["brandA"], "lock"),
             ("Relationships", "12", "connections", C["amber"], "people"),
             ("Engagement", "92%", "high", C["green"], "chart"),
             ("Moderation", "99.4%", "pass rate", C["cyan"], "shieldok")]
    for i, (lbl, val, sub, col, ic) in enumerate(tiles):
        o += tile(IX + i * (tw + 20), IY, tw, 96, lbl, val, sub, col, ic)
    y2 = IY + 96 + 22
    lw = IW * 0.64
    rw = IW - lw - 20
    ph = 268
    o += panel(IX, y2, lw, ph, "Conversations over time", right="last 12 weeks")
    o.append(areachart(IX + 20, y2 + 52, lw - 40, ph - 96,
                       [12, 18, 15, 24, 30, 27, 38, 44, 40, 52, 61, 58], C["brandA"]))
    o.append(text(IX + 20, y2 + ph - 16, "wk 1", 9, C["t3"], 500))
    o.append(text(IX + lw - 20, y2 + ph - 16, "now", 9, C["t3"], 500, "end"))
    o += panel(IX + lw + 20, y2, rw, ph, "Ava")
    acx = IX + lw + 20 + rw / 2
    o.append(f'<circle cx="{acx}" cy="{y2+96}" r="42" fill="url(#orb)"/>')
    o.append(icon("person", acx, y2 + 94, "rgba(255,255,255,0.92)", 1.9))
    o.append(f'<circle cx="{acx}" cy="{y2+96}" r="48" fill="none" stroke="url(#gBrand)" stroke-width="3"/>')
    o.append(text(acx, y2 + 168, "Ava · AI Version Me", 12.5, C["txt"], 700, "middle"))
    o.append(status_dot(acx + 44, y2 + 190, "Online", "on"))
    o.append(text(acx - 52, y2 + 194, "Identity 98.9%", 10, C["t2"], 600))
    y3 = y2 + ph + 22
    bh = CONTENT_Y + CONTENT_H - PAD - y3
    o += panel(IX, y3, lw, bh, "Recent activity", right="live")
    rows = [[("MESSAGE", C["brandA"], 700), "“Been thinking about the garden.”", ("2m", C["t2"], 500)],
            [("MEMORY", C["green"], 700), "New: started keto (Apr 20)", ("1h", C["t2"], 500)],
            [("RELATION", C["amber"], 700), "Sarah → tone set to Supportive", ("3h", C["t2"], 500)],
            [("POST", C["cyan"], 700), "“Tomatoes are in — finally.”", ("5h", C["t2"], 500)]]
    o.append(table(IX + 18, y3 + 44, lw - 36,
                   [("TYPE", 0.2, "start"), ("DETAIL", 0.66, "start"), ("WHEN", 0.14, "end")], rows, rowh=32))
    o += panel(IX + lw + 20, y3, rw, bh, "Relationships")
    ty = y3 + 44
    for init, name, rel, col, tone in [("D", "David", "Owner", C["brandA"], ("You", "brand")),
                                       ("S", "Sarah", "Daughter", C["amber"], ("Supportive", "good")),
                                       ("E", "Dr. Emily", "Therapist", C["pink"], ("Prof.", "gold"))]:
        o.append(f'<circle cx="{IX+lw+58}" cy="{ty+18}" r="14" fill="{A(col,0.20)}" stroke="{col}" stroke-width="1.2"/>')
        o.append(text(IX + lw + 58, ty + 23, init, 12, col, 800, "middle"))
        o.append(text(IX + lw + 80, ty + 15, name, 11.5, C["txt"], 700))
        o.append(text(IX + lw + 80, ty + 30, rel, 9.5, C["t2"], 500))
        o.append(pill(IX + lw + 20 + rw - 16, ty + 18, tone[0], tone[1]))
        ty += 44
    return o


def v_conversation():
    o = []
    lw = IW * 0.62
    rw = IW - lw - 20
    hh = CONTENT_H - 2 * PAD
    o += panel(IX, IY, lw, hh, "Chat with Ava", right="every response explained")
    cy = IY + 56
    # AI bubble
    o.append(rrect(IX + 24, cy, lw * 0.62, 62, 14, "rgba(255,255,255,0.04)", C["line"], 1))
    for i, ln in enumerate(["Hey David, I noticed you haven't checked in this",
                            "week. Want to talk about the garden? 🌱"]):
        o.append(text(IX + 40, cy + 26 + i * 18, ln, 11, C["txt"], 400))
    cy += 82
    # user bubble (right)
    uw = lw * 0.55
    o.append(rrect(IX + lw - 24 - uw, cy, uw, 44, 14, "url(#gBrand)"))
    o.append(text(IX + lw - 40, cy + 20, "Hey Ava! I've been busy,", 10.5, "#fff", 500, "end"))
    o.append(text(IX + lw - 40, cy + 35, "but thinking about you.", 10.5, "#fff", 500, "end"))
    cy += 64
    o.append(rrect(IX + 24, cy, lw * 0.66, 62, 14, "rgba(255,255,255,0.04)", C["line"], 1))
    for i, ln in enumerate(["The tomatoes should be ready by now — you planted",
                            "them in March. Want me to remind you to harvest?"]):
        o.append(text(IX + 40, cy + 26 + i * 18, ln, 11, C["txt"], 400))
    # input bar
    iby = IY + hh - 60
    o.append(rrect(IX + 24, iby, lw - 48, 40, 12, "#0d0a24", C["line"], 1))
    o.append(text(IX + 40, iby + 25, "Type a message…", 11, C["t3"]))
    o.append(f'<circle cx="{IX+lw-46}" cy="{iby+20}" r="14" fill="url(#gBrand)"/>')
    o.append(text(IX + lw - 46, iby + 25, "→", 14, "#fff", 800, "middle"))
    # right: AI context
    o += panel(IX + lw + 20, IY, rw, hh, "AI context")
    dx = IX + lw + 38
    dw = rw - 36
    o.append(rrect(dx, IY + 46, dw, 52, 11, A(C["brandA"], 0.08), C["brandA"], 1))
    o.append(icon("lock", dx + 22, IY + 72, C["brandA"], 0.8))
    o.append(text(dx + 42, IY + 68, "Why this response?", 11.5, C["txt"], 700))
    o.append(text(dx + 42, IY + 84, "grounded, explainable, in-persona", 9.5, C["t2"], 500))
    o.append(text(dx, IY + 128, "CONTEXT USED", 8.5, C["t3"], 700, "start", 0.4))
    cy2 = IY + 146
    for ln in ["Garden memories", "Past conversations", "Relationship tone: warm",
               "Personality: warm + curious"]:
        o.append(f'<path d="M{dx} {cy2} l{3} {3.4} {6} -{6.6}" fill="none" stroke="{C["green"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(text(dx + 18, cy2 + 4, ln, 10.5, C["txt"], 500))
        cy2 += 30
    o.append(rrect(dx, cy2 + 8, dw, 46, 11, "rgba(255,255,255,0.03)", C["line"], 1))
    o.append(icon("finger", dx + 22, cy2 + 31, C["cyan"], 0.8))
    o.append(text(dx + 42, cy2 + 27, "Persona signature", 11, C["txt"], 650))
    o.append(text(dx + 42, cy2 + 42, "invariant across every form", 9.5, C["t2"], 500))
    return o


def v_relationships():
    o = []
    lw = IW * 0.62
    rw = IW - lw - 20
    hh = CONTENT_H - 2 * PAD
    o += panel(IX, IY, lw, hh, "People in Ava's life", right="12 relationships")
    rows = [[("D", "David", C["brandA"]), "Owner", ("Direct", C["txt"], 500), "now"],
            [("S", "Sarah", C["amber"]), "Daughter", ("Supportive", C["green"], 600), "3h"],
            [("J", "John", C["cyan"]), "Friend", ("Casual", C["cyan"], 500), "1d"],
            [("E", "Dr. Emily", C["pink"]), "Therapist", ("Professional", C["gold"], 600), "2d"],
            [("M", "Mom", C["green"]), "Family", ("Warm", C["amber"], 600), "4d"]]
    # custom rows with avatar
    o.append(f'<line x1="{IX+18}" y1="{IY+68}" x2="{IX+lw-18}" y2="{IY+68}" stroke="{C["line"]}" stroke-width="1"/>')
    for hlbl, frac, al in [("PERSON", 0.34, "start"), ("RELATIONSHIP", 0.24, "start"),
                           ("TONE", 0.24, "start"), ("LAST", 0.18, "end")]:
        pass
    o.append(text(IX + 60, IY + 60, "PERSON", 9.5, C["t3"], 700, "start", 0.4))
    o.append(text(IX + lw * 0.40, IY + 60, "RELATIONSHIP", 9.5, C["t3"], 700, "start", 0.4))
    o.append(text(IX + lw * 0.62, IY + 60, "TONE", 9.5, C["t3"], 700, "start", 0.4))
    o.append(text(IX + lw - 18, IY + 60, "LAST", 9.5, C["t3"], 700, "end", 0.4))
    ry = IY + 80
    for (init, name, col), rel, tone, last in rows:
        o.append(f'<circle cx="{IX+34}" cy="{ry+16}" r="14" fill="{A(col,0.20)}" stroke="{col}" stroke-width="1.2"/>')
        o.append(text(IX + 34, ry + 21, init, 12, col, 800, "middle"))
        o.append(text(IX + 60, ry + 21, name, 11.5, C["txt"], 650))
        o.append(text(IX + lw * 0.40, ry + 21, rel, 10.5, C["t2"], 500))
        o.append(text(IX + lw * 0.62, ry + 21, tone[0], 10.5, tone[1], tone[2]))
        o.append(text(IX + lw - 18, ry + 21, last, 10, C["t2"], 500, "end"))
        ry += 44
        o.append(f'<line x1="{IX+18}" y1="{ry}" x2="{IX+lw-18}" y2="{ry}" stroke="{A(C["line"],0.45)}" stroke-width="1"/>')
    # right: detail
    o += panel(IX + lw + 20, IY, rw, hh, "Relationship detail")
    dx = IX + lw + 38
    dw = rw - 36
    o.append(f'<circle cx="{dx+26}" cy="{IY+70}" r="22" fill="{A(C["amber"],0.20)}" stroke="{C["amber"]}" stroke-width="1.4"/>')
    o.append(text(dx + 26, IY + 76, "S", 18, C["amber"], 800, "middle"))
    o.append(text(dx + 60, IY + 64, "Sarah", 15, C["txt"], 750))
    o.append(text(dx + 60, IY + 82, "Daughter · nickname “kiddo”", 10, C["t2"], 500))
    for k, val in [("Tone", "Supportive, warm"), ("Boundaries", "finances (blocked)"),
                   ("Memory", "48 shared entries"), ("Engagement", "high · 0.86"),
                   ("Last talked", "3 hours ago")]:
        pass
    fy = IY + 108
    for k, val, col in [("Tone", "Supportive, warm", C["green"]),
                        ("Boundaries", "finances — blocked", C["red"]),
                        ("Shared memory", "48 entries", C["brandA"]),
                        ("Engagement", "high · 0.86", C["amber"]),
                        ("Age & status", "verified adult", C["cyan"])]:
        o.append(rrect(dx, fy, dw, 52, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(text(dx + 16, fy + 21, k.upper(), 8.5, C["t3"], 700, "start", 0.4))
        o.append(text(dx + 16, fy + 39, val, 11.5, col, 650))
        fy += 60
    return o


def v_memory():
    o = []
    lw = IW * 0.64
    rw = IW - lw - 20
    hh = CONTENT_H - 2 * PAD
    o += panel(IX, IY, lw, hh, "Memory vault", right="1,429 items · sealed")
    rows = [[("STORY", C["brandA"], 700), "Life stories & events", "245", "sealed"],
            [("VOICE", C["pink"], 700), "Voice notes", "38", "sealed"],
            [("PHOTO", C["cyan"], 700), "Photos", "122", "sealed"],
            [("CHAT", C["amber"], 700), "Conversations", "1,024", "sealed"],
            [("KNOW", C["green"], 700), "Knowledge entries", "156", "sealed"]]
    o.append(table(IX + 18, IY + 46, lw - 36,
                   [("KIND", 0.16, "start"), ("SOURCE", 0.48, "start"),
                    ("ITEMS", 0.18, "end"), ("STATUS", 0.18, "end")],
                   [[r[0], r[1], (r[2], C["txt"], 700), (r[3], C["green"], 600)] for r in rows], rowh=42))
    o += panel(IX + lw + 20, IY, rw, hh, "Storage")
    dx = IX + lw + 38
    dw = rw - 36
    o.append(rrect(dx, IY + 46, dw, 60, 12, A(C["green"], 0.08), C["green"], 1))
    o.append(icon("shieldok", dx + 26, IY + 76, C["green"], 1.1))
    o.append(text(dx + 52, IY + 70, "LOCAL VAULT", 12, C["txt"], 700))
    o.append(text(dx + 52, IY + 86, "AES-256-GCM protected", 10, C["green"], 500))
    for k, val, col in [("Total items", "1,429", C["brandA"]), ("On disk", "212 MB ciphertext", C["cyan"]),
                        ("Cloud contribution", "off", C["t2"])]:
        pass
    fy = IY + 122
    for k, val, col in [("Total items", "1,429", C["brandA"]),
                        ("On disk", "212 MB", C["cyan"]),
                        ("Cloud contribution", "OFF", C["red"])]:
        o.append(rrect(dx, fy, dw, 44, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(text(dx + 16, fy + 27, k, 11, C["t2"], 600))
        o.append(text(dx + dw - 16, fy + 27, val, 12, col, 700, "end"))
        fy += 52
    o.append(button(dx, fy + 6, dw, "Export everything", "brand", 40))
    o.append(button(dx, fy + 54, dw, "Delete everything", "danger", 40))
    return o


def v_marketplace():
    o = []
    lw = IW * 0.58
    rw = IW - lw - 20
    hh = CONTENT_H - 2 * PAD
    o += panel(IX, IY, lw, hh, "Discover profiles", right="marketplace")
    cy = IY + 50
    cards = [("chart", "green", "Financial Expert AI", "Wealth advisor & planning", 4.9, "125"),
             ("heart", "pink", "Wellness Coach", "Mental & physical health", 4.8, "98"),
             ("star2", "amber", "Creator Assistant", "Brand & content expert", 4.9, "210"),
             ("book", "cyan", "Historical Expert", "History & civilization", 4.7, "76")]
    for ic, col, k, s, rt, cnt in cards:
        c = ACCENT[col]
        o.append(rrect(IX + 24, cy, lw - 48, 62, 12, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(f'<circle cx="{IX+54}" cy="{cy+31}" r="18" fill="{A(c,0.18)}" stroke="{c}" stroke-width="1.2"/>')
        o.append(icon(ic, IX + 54, cy + 31, c, 0.95))
        o.append(text(IX + 84, cy + 26, k, 12.5, C["txt"], 700))
        o.append(text(IX + 84, cy + 42, s, 10, C["t2"], 500))
        o.append(stars(IX + lw - 150, cy + 26, rt, C["gold"], 0.66))
        o.append(text(IX + lw - 150, cy + 46, f"{rt} · ▲{cnt}", 9.5, C["gold"], 600))
        cy += 72
    o += panel(IX + lw + 20, IY, rw, hh, "Your licensing", right="earnings")
    dx = IX + lw + 38
    dw = rw - 36
    lic = [("chat", "brand", "Consult", "$20 / session"),
           ("sliders", "amber", "Fine Tune", "$499 / license"),
           ("people", "pink", "Clone Agent", "Negotiated")]
    ly = IY + 46
    for ic, col, k, price in lic:
        o.append(rrect(dx, ly, dw, 52, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(dx + 12, ly + 9, ic, ACCENT[col]))
        o.append(text(dx + 56, ly + 23, k, 12, C["txt"], 700))
        o.append(text(dx + 56, ly + 39, "active offer", 9.5, C["t2"], 500))
        o.append(text(dx + dw - 14, ly + 31, price, 11.5, ACCENT[col], 700, "end"))
        ly += 62
    o.append(rrect(dx, ly + 4, dw, 66, 12, A(C["green"], 0.08), C["green"], 1))
    o.append(text(dx + 16, ly + 28, "Earnings this month", 10.5, C["t2"], 600))
    o.append(text(dx + 16, ly + 54, "$1,840", 22, C["green"], 800))
    o.append(text(dx + dw - 16, ly + 52, "18 grants", 10, C["t2"], 500, "end"))
    return o


def v_control():
    o = []
    lw = (IW - 20) / 2
    hh = CONTENT_H - 2 * PAD
    o += panel(IX, IY, lw, hh, "Privacy & permissions")
    dx = IX + 20
    dw = lw - 40
    def togrow(y, label, sub, on):
        r = [rrect(dx, y, dw, 46, 11, "rgba(255,255,255,0.03)", C["line"], 1)]
        r.append(text(dx + 16, y + 22, label, 11.5, C["txt"], 650))
        r.append(text(dx + 16, y + 37, sub, 9.5, C["t2"], 500))
        bg = C["green"] if on else "#2a2450"
        kx = dx + dw - 40 + 16 if on else dx + dw - 40 + 2
        r.append(rrect(dx + dw - 42, y + 13, 34, 20, 10, bg))
        r.append(f'<circle cx="{kx+8}" cy="{y+23}" r="8" fill="#fff"/>')
        return r
    ty = IY + 46
    for lbl, sub, on in [("Offline mode", "nothing leaves this device", True),
                         ("Cloud contribution", "anonymized, previewable", False),
                         ("Camera", "for perceive & guide", True),
                         ("Microphone", "for voice replies", True),
                         ("Location", "for local providers", False)]:
        o += togrow(ty, lbl, sub, on)
        ty += 54
    o.append(rrect(dx, ty + 6, dw, 44, 11, A(C["red"], 0.08), C["red"], 1))
    o.append(icon("warn", dx + 24, ty + 28, C["red"], 0.85))
    o.append(text(dx + 46, ty + 25, "Delete my profile", 11.5, C["txt"], 650))
    o.append(text(dx + 46, ty + 40, "erased locally & in the vault", 9.5, C["t2"], 500))
    # right: embodiments & surfaces
    o += panel(IX + lw + 20, IY, lw, hh, "Embodiments & surfaces")
    ex = IX + lw + 20 + 20
    ew = lw - 40
    rows = [("phone", "iPhone", "on", "ONLINE"), ("watch", "Apple Watch", "on", "ONLINE"),
            ("headset", "AR Headset", "off", "OFFLINE"), ("robot", "Robot", "avail", "AVAILABLE"),
            ("speaker", "Smart Speaker", "on", "ONLINE")]
    ey = IY + 46
    for ic, k, tone, lbl in rows:
        o.append(rrect(ex, ey, ew, 46, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(ex + 10, ey + 6, ic, C["brandA"]))
        o.append(text(ex + 54, ey + 28, k, 12, C["txt"], 650))
        o.append(status_dot(ex + ew - 14, ey + 23, lbl, tone))
        ey += 54
    o.append(rrect(ex, ey + 4, ew, 44, 11, A(C["brandA"], 0.08), C["brandA"], 1))
    o.append(icon("finger", ex + 24, ey + 26, C["brandA"], 0.9))
    o.append(text(ex + 46, ey + 22, "Identity signature", 11, C["txt"], 650))
    o.append(text(ex + 46, ey + 38, "98.9% consistent across forms", 9.5, C["t2"], 500))
    return o


VIEWS = [
    (1, "Home", "Home", v_home),
    (2, "Conversation", "Conversation", v_conversation),
    (3, "Relationships", "Relationships", v_relationships),
    (4, "Memory Vault", "Memory", v_memory),
    (5, "Marketplace & Licensing", "Marketplace", v_marketplace),
    (6, "Control Center", "Control", v_control),
]


def render(title, nav, fn):
    o = frame(title, nav)
    o += fn()
    o += close()
    return "".join(o)


def main():
    global PLATFORM_D
    total = 0
    for plat, sub in (("macos", ""), ("windows", "windows")):
        PLATFORM_D = plat
        outdir = OUT if not sub else os.path.join(OUT, sub)
        os.makedirs(outdir, exist_ok=True)
        for num, title, nav, fn in VIEWS:
            slug = title.lower().replace(" & ", "-").replace(" ", "-")
            with open(os.path.join(outdir, f"{num:02d}-{slug}.svg"), "w") as f:
                f.write(render(title, nav, fn))
            total += 1
    PLATFORM_D = "macos"
    print(f"generated {total} desktop screens ({len(VIEWS)} × 2 platforms)")


if __name__ == "__main__":
    main()
