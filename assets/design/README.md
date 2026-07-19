# QRME design system

Hand-built vector assets for the QRME product family. Everything here is
self-contained SVG — no external fonts, images, or scripts — so the assets
render identically in a browser, a README, and any converter.

## Philosophy

- **One world, three products.** QRME, JIM-mini, and PDI share a night-indigo
  universe; each product gets one accent identity inside it (QRME amber,
  JIM-mini guardian green, PDI vault cyan) so the family reads as related
  without blurring together.
- **Warmth over tech-noir.** The subject is people and their relationships;
  gradients glow instead of glare, figures are soft silhouettes, and data is
  drawn as constellations and threads rather than circuitry.
- **Honest illustration.** Every diagram depicts something the code actually
  does — the moderation gates, the consent gate, the vault key path. If a
  feature is structural-only, the caption says so.
- **Craft in layers.** Each piece is built background → glow → subject →
  detail → vignette, with `feGaussianBlur` under-glows and a radial vignette
  to give flat SVG real depth.

## Palette

| Token | Hex | Role |
|---|---|---|
| Indigo deep | `#10123A` | Backgrounds (darkest stop) |
| Indigo | `#1B1D4E` | Primary surface |
| Indigo soft | `#2E3170` | Cards, panels |
| Silver | `#C9CDD8` | Secondary figures, body text |
| Muted | `#8B90A8` | Captions, de-emphasis |
| Amber | `#E8A34D` | QRME accent — warmth, relationships, action |
| Cream | `#F4E3C8` | Headlines, highlights |
| Guardian green | `#7BC47F` | JIM-mini accent — vitals, safety |
| Vault cyan | `#9FD8E8` | PDI accent — encryption, audit |
| Alert red | `#D96A6A` | Escalation, rejection |
| Hold gold | `#E8C34D` | Pending / review states |

Relationship warmth is graded amber → cream → silver (family → friend →
stranger); severity is graded green → gold → red.

## File conventions

- `NN-name.svg`, numbered in narrative order; `00-cover.svg` is the repo
  hero at **1280×640** (GitHub's social-preview ratio).
- Root element: `viewBox` + explicit `width`/`height`, `role="img"`, and a
  first-child `<title>` plus `<desc>` for accessibility (screen readers and
  the gallery's alt text mirror them).
- Gradient/filter ids are prefixed per file (e.g. `qbg`, `hvign`) so any two
  files can be inlined into one document without id collisions.
- Text uses `Helvetica, Arial, sans-serif` only — universally available, so
  no font loading and no licensing.
- Wide content scrolls; nothing depends on JavaScript.

## Exporting crisp PNGs

SVG is the source of truth — export PNGs at the size you need rather than
scaling a small one up. Recommended sizes: **512 px** (avatars, favicons via
downscale), **1024 px** (README embeds, docs), **2048 px** (slides, social
cards), **4096 px** (print, press).

```bash
# rsvg-convert (librsvg) — fast and faithful
rsvg-convert -w 2048 01-app-icon.svg -o icon@2048.png

# Inkscape
inkscape 00-cover.svg -w 2048 -o cover@2048.png

# Headless Chrome (no extra installs)
chrome --headless --screenshot=cover.png --window-size=2048,1024 00-cover.svg
```

For GitHub's social preview, export `00-cover.svg` at 2048×1024 (GitHub wants
a PNG ≥ 1280×640) and upload it under *Settings → Social preview*.

## Gallery

Open [`gallery.html`](gallery.html) in a browser for the full annotated set.
