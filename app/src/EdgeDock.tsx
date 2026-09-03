import { useRef, useState } from "react";
import { Help } from "./Help";
import { WatchLights } from "./WatchLights";
import { t as tr, visitorLang } from "./l10n";

/**
 * The edge dock: every control the shell floats over the screens, as one
 * stack of tabs on the right edge of the glass.
 *
 *     asked     "they seem to be getting in the way a lot — maybe
 *               horizontal tabs on the side of the screen that can be
 *               moved up or down that you click onto expand"
 *     mattered  three separate corners, each with its own widget, each
 *               parked over whatever a screen had put there
 *
 * The help bubble sat bottom-right, the agent lights bottom-left, the
 * footsteps counter top-right — three fixed things in three corners, and
 * a phone has no empty corner. Field photographs showed the lights over
 * the Home and Chat tabs, the bubble over Campaigns, the minimized light
 * as a disc on the room's record card, and the counter over the room's
 * way out. Each was moved a little, twice, and the next screen found it
 * again.
 *
 * So they share one edge. Each control is a tab that protrudes from the
 * right side of the window; pressing a tab opens its panel beside it,
 * pressing again (or another tab) closes it; and the whole stack slides
 * up or down by its grip, with the position remembered per device. A
 * person who finds it in the way moves it once, and it stays moved.
 *
 * Two tabs: the help box, and the agent lights — a stoplight, minimized,
 * that opens to the round watch-face window ("I still like the circle
 * version as the full screen window for running agents"). The footsteps
 * count is gone: everyone with an account shows in the community's
 * Discover, and a number beside a glyph said less than that page does.
 *
 * Only one panel is open at a time — the dock owns that, so the panels
 * cannot open over each other the way independent widgets could.
 */

const Y_KEY = "qrme.dock.y";
//: Where the dock's top sits, as a share of the window's height. Low on
//: the glass by default: the room's own dock of panels lives at the
//: middle of the right edge, and the loudness rail at exactly half, so
//: the shell's tabs stand under both rather than on them.
const Y_DEFAULT = 72;
const Y_MIN = 4;
const Y_MAX = 90;
//: A press that travels less than this is a press, not a move.
const SLOP_PX = 4;

export type DockTab = "help" | "lights";

function remembered(): number {
  try {
    const v = Number(localStorage.getItem(Y_KEY));
    if (Number.isFinite(v) && v >= Y_MIN && v <= Y_MAX) return v;
  } catch { /* a browser that blocks storage keeps the default */ }
  return Y_DEFAULT;
}

function clamp(v: number): number {
  return Math.min(Y_MAX, Math.max(Y_MIN, v));
}

export function EdgeDock() {
  const lang = visitorLang();
  const [y, setY] = useState(remembered);
  const [open, setOpen] = useState<DockTab | null>(null);
  const drag = useRef<{ startY: number; startPct: number; moved: boolean }
                      | null>(null);

  const toggle = (tab: DockTab) => setOpen((cur) => (cur === tab ? null : tab));

  function remember(pct: number) {
    try { localStorage.setItem(Y_KEY, String(Math.round(pct))); }
    catch { /* not remembered, still moved */ }
  }

  // The grip is the one thing that moves the stack. The tabs only press:
  // a control that is both a button and a handle answers a slow thumb
  // with the wrong one of the two, and the report that shaped this was
  // about things being in the way, not about reaching them faster.
  function down(e: React.PointerEvent<HTMLButtonElement>) {
    drag.current = { startY: e.clientY, startPct: y, moved: false };
    e.currentTarget.setPointerCapture(e.pointerId);
  }
  function move(e: React.PointerEvent<HTMLButtonElement>) {
    const d = drag.current;
    if (!d) return;
    const dy = e.clientY - d.startY;
    if (!d.moved && Math.abs(dy) < SLOP_PX) return;
    d.moved = true;
    setY(clamp(d.startPct + (dy / window.innerHeight) * 100));
  }
  function up(e: React.PointerEvent<HTMLButtonElement>) {
    const d = drag.current;
    drag.current = null;
    if (!d) return;
    e.currentTarget.releasePointerCapture(e.pointerId);
    if (d.moved) remember(clamp(d.startPct + ((e.clientY - d.startY)
                                                / window.innerHeight) * 100));
  }
  // The same move from a keyboard: the grip is a button, and a button
  // that only answers a pointer is a control half the room cannot use.
  function key(e: React.KeyboardEvent<HTMLButtonElement>) {
    const step = e.key === "ArrowUp" ? -5 : e.key === "ArrowDown" ? 5 : 0;
    if (!step) return;
    e.preventDefault();
    const next = clamp(y + step);
    setY(next);
    remember(next);
  }

  // A panel hangs off the dock's top edge while the dock is high on the
  // glass, and off its bottom edge once it is low — so the panel opens
  // toward the room there is, never off the bottom of a phone.
  const low = y > 50;
  return (
    <div className={"edge-dock" + (low ? " low" : "") + (open ? " open" : "")}
         style={{ top: `${y}%`, ["--dock-y" as string]: `${y}vh` }}
         data-dock-y={Math.round(y)}>
      <button className="edge-grip" type="button"
              aria-label={tr("dock.move", lang)} title={tr("dock.move", lang)}
              onPointerDown={down} onPointerMove={move}
              onPointerUp={up} onPointerCancel={up} onKeyDown={key}>
        <span aria-hidden="true">⋮</span>
      </button>
      <Help open={open === "help"} onToggle={() => toggle("help")} />
      <WatchLights open={open === "lights"}
                   onToggle={() => toggle("lights")} />
    </div>
  );
}
