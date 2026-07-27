"""Generate the emblems an anonymous profile can wear instead of a face.

One per industry the platform already models (`exchange.INDUSTRIES`), so the
set is not a new vocabulary invented for pictures — it is the same list the
marketplace, the knowledge packs and the work agreements already use. A field
that can be worked in can be signalled.

Every emblem keeps the **same silhouette** as the plain one, with a field glyph
badged onto it and a tint. That is deliberate: an anonymous profile has to read
as anonymous at a glance, from across a roster, before anybody parses which
symbol it carries. The emblem says *what I do*; the silhouette underneath still
says *you do not get to know who I am*.

Run: python3 tools/build_emblems.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qrme import exchange  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "qrme", "assets", "figures")

# A tint per field, and a glyph drawn in a 24×24 box centred on (12, 12).
# Kept simple on purpose: these are read at 40px on a roster row, where a
# detailed drawing becomes a smudge and a bold shape stays legible.
FIELDS: dict[str, tuple[str, str]] = {
    "software": ("#5B8CFF",
                 '<path d="M9 7 L4 12 L9 17 M15 7 L20 12 L15 17" fill="none" '
                 'stroke="#fff" stroke-width="2.2" stroke-linecap="round" '
                 'stroke-linejoin="round"/>'),
    "design": ("#C77DFF",
               '<circle cx="12" cy="9" r="3.4" fill="none" stroke="#fff" '
               'stroke-width="2.1"/><path d="M8 19 L12 12 L16 19 Z" '
               'fill="#fff"/>'),
    "writing": ("#F2B544",
                '<path d="M6 18 L8 13 L16 5 L19 8 L11 16 Z" fill="#fff"/>'
                '<path d="M6 20 H19" stroke="#fff" stroke-width="2" '
                'stroke-linecap="round"/>'),
    "audio": ("#3ED6A6",
              '<path d="M5 12 V12 M8 8 V16 M11 5 V19 M14 8 V16 M17 10 V14 '
              'M20 11 V13" stroke="#fff" stroke-width="2.2" '
              'stroke-linecap="round"/>'),
    "video": ("#FF6FA5",
              '<rect x="4" y="7" width="12" height="10" rx="2.5" fill="#fff"/>'
              '<path d="M18 9.5 L21 7.5 V16.5 L18 14.5 Z" fill="#fff"/>'),
    "photography": ("#7BD8FF",
                    '<rect x="3.5" y="7" width="17" height="11" rx="2.5" '
                    'fill="#fff"/><circle cx="12" cy="12.5" r="3.4" '
                    'fill="#1B1838"/><rect x="9" y="4.5" width="6" '
                    'height="2.6" rx="1" fill="#fff"/>'),
    "engineering": ("#9AA6C4",
                    '<path d="M12 4.5 L18.5 8.2 V15.8 L12 19.5 L5.5 15.8 '
                    'V8.2 Z" fill="none" stroke="#fff" stroke-width="2.2" '
                    'stroke-linejoin="round"/><circle cx="12" cy="12" '
                    'r="2.6" fill="#fff"/>'),
    "trades": ("#F58B4C",
               '<path d="M16.5 4.5 a4.5 4.5 0 1 0 3.6 6.6 L7.5 19.5 '
               'a2.1 2.1 0 0 1-3-3 L13 8.4 a4.5 4.5 0 0 1 3.5-3.9 Z" '
               'fill="#fff"/>'),
    "finance": ("#4ED17A",
                '<path d="M5 19 V13 H9 V19 Z M10.5 19 V8 H14.5 V19 Z '
                'M16 19 V4.5 H20 V19 Z" fill="#fff"/>'),
    "legal": ("#B8C4E0",
              '<path d="M12 4 V20 M6 20 H18" stroke="#fff" stroke-width="2.2" '
              'stroke-linecap="round"/><path d="M4 8 H20" stroke="#fff" '
              'stroke-width="2.2" stroke-linecap="round"/>'
              '<circle cx="5.5" cy="12" r="2.4" fill="#fff"/>'
              '<circle cx="18.5" cy="12" r="2.4" fill="#fff"/>'),
    "healthcare": ("#FF7A7A",
                   '<path d="M9.5 4 H14.5 V9.5 H20 V14.5 H14.5 V20 H9.5 '
                   'V14.5 H4 V9.5 H9.5 Z" fill="#fff"/>'),
    "education": ("#6FD3F5",
                  '<path d="M12 5 L21 9 L12 13 L3 9 Z" fill="#fff"/>'
                  '<path d="M6.5 11 V16 c0 2 11 2 11 0 V11" fill="none" '
                  'stroke="#fff" stroke-width="2.1" stroke-linecap="round"/>'),
    "marketing": ("#FFB020",
                  '<path d="M4 10 V14 H8 L16 19 V5 L8 10 Z" fill="#fff"/>'
                  '<path d="M18.5 9 a4 4 0 0 1 0 6" fill="none" '
                  'stroke="#fff" stroke-width="2.1" stroke-linecap="round"/>'),
    "research": ("#8E9BFF",
                 '<circle cx="10.5" cy="10.5" r="5.5" fill="none" '
                 'stroke="#fff" stroke-width="2.3"/><path d="M14.8 14.8 '
                 'L20 20" stroke="#fff" stroke-width="2.4" '
                 'stroke-linecap="round"/>'),
    "manufacturing": ("#A3B1CC",
                      '<path d="M4 19 V10 L9.5 13.5 V10 L15 13.5 V10 L20.5 '
                      '13.5 V19 Z" fill="#fff"/>'),
    "other": ("#7C74D6",
              '<circle cx="12" cy="12" r="3.4" fill="#fff"/>'
              '<circle cx="12" cy="12" r="7.5" fill="none" stroke="#fff" '
              'stroke-width="2" stroke-dasharray="3 3.4"/>'),
}

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" \
width="200" height="200" role="img" aria-label="Anonymous — {label}">
  <!-- Generated by tools/build_emblems.py. Do not edit by hand.

       The same silhouette every anonymous profile wears, with a field glyph
       badged on. The figure stays identical across all of them so that
       "anonymous" is what reads first, from across a roster, before anybody
       parses which symbol it carries. The emblem says what somebody does; the
       silhouette underneath still says you do not get to know who they are. -->
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2A2550"/>
      <stop offset="1" stop-color="#1B1838"/>
    </linearGradient>
  </defs>
  <rect width="200" height="200" fill="url(#bg)"/>
  <circle cx="100" cy="78" r="30" fill="#6C63C4"/>
  <path d="M46 168 c0 -32 24 -52 54 -52 s54 20 54 52 z" fill="#6C63C4"/>
  <circle cx="150" cy="150" r="36" fill="{tint}" stroke="#1B1838" \
stroke-width="6"/>
  <g transform="translate(126 126) scale(2)">{glyph}</g>
</svg>
"""


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    missing = set(exchange.INDUSTRIES) - set(FIELDS)
    extra = set(FIELDS) - set(exchange.INDUSTRIES)
    if missing or extra:
        raise SystemExit(
            "the emblem set and exchange.INDUSTRIES have drifted — "
            f"missing {sorted(missing)}, extra {sorted(extra)}. They mirror "
            "each other on purpose: a field that can be worked in is a field "
            "that can be signalled.")

    for key, (tint, glyph) in FIELDS.items():
        path = os.path.join(OUT, f"emblem-{key}.svg")
        with open(path, "w") as fh:
            fh.write(TEMPLATE.format(label=key, tint=tint, glyph=glyph))
    print(f"generated {len(FIELDS)} emblems into {OUT}")


if __name__ == "__main__":
    main()
