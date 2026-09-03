import { useCallback, useEffect, useState } from "react";
import { api, type WatchFace } from "./api";
import { t as tr, visitorLang } from "./l10n";
import { useSession } from "./store";

/**
 * The agent task lights, always on screen — the same glanceable payload
 * the wrist gets (GET /profiles/{id}/watch), so the owner never has to go
 * looking for whether an agent is working (green), waiting on them
 * (amber), or stopped (red).
 *
 * Mounted from the edge dock, like Help: "on every screen" is a property
 * of the shell. The tab is the minimized state — a stoplight, in the
 * owner's words, wearing the worst light's colour on its edge — and
 * pressing it opens the round watch-face window beside it: three lights,
 * three counts, the approval line, the size and shape of the wrist's own
 * face ("I still like the circle version as the full screen window for
 * running agents").
 *
 * And the window elaborates when asked. Each row is a press: pressing
 * "2 working" lists the two, by the goal each was given, so the person
 * can see *which* agent is hung up, running or stopped without leaving
 * the screen they are on. The face grows from a circle to an oval to hold
 * the names and shrinks back when the row is pressed again. The full
 * agent roster with its controls stays on the Agents screen.
 *
 * The round window was once pinned bottom-left with a minimize control
 * that folded it to a dot, and field photographs showed the dot — the
 * thing meant to be out of the way — parked on the room's record card
 * and on the last three tabs of the desktop sidebar. On the dock the
 * minimized state is a tab on the edge, movable with the rest.
 */

const POLL_MS = 15000;

const COLORS = { green: "#43e08a", amber: "#ffb84d", red: "#e0687a" };
type Tone = keyof typeof COLORS;

function worst(face: WatchFace): Tone {
  if (face.summary.stopped > 0 || face.chip.light === "red") return "red";
  if (face.summary.needing_assistance > 0) return "amber";
  return "green";
}

// The wire says "orange" where the screen says amber — the wrist's word
// for the same light, kept on the wire because the watches read it.
function tone(light: string): Tone {
  return light === "orange" ? "amber" : light === "red" ? "red" : "green";
}

/** Who stands under each light: the agents by goal, the robots by name,
 *  and the profile itself when its own light is the one that is not
 *  green — the summary counts it, so the elaboration names it. */
function under(face: WatchFace, t: Tone): string[] {
  const out: string[] = [];
  for (const a of face.agents ?? []) {
    if (a.light === "done" || a.light === "idle") continue;
    if (tone(a.light) === t) out.push(a.goal);
  }
  for (const r of face.robots ?? []) {
    if (r.light === "idle") continue;
    if (tone(r.light) === t) out.push(r.name);
  }
  const own = tone(face.chip.light);
  if (own !== "green" && own === t) {
    out.push(face.chip.pending_approvals > 0
      ? `${face.chip.display_name} — ${face.chip.pending_approvals} approval${face.chip.pending_approvals === 1 ? "" : "s"} waiting`
      : `${face.chip.display_name} — ${face.chip.status}`);
  }
  return out;
}

export function WatchLights({ open, onToggle }:
                            { open: boolean; onToggle: () => void }) {
  const lang = visitorLang();
  const { session } = useSession();
  const [face, setFace] = useState<WatchFace | null>(null);
  // The first fetch failing is not a blip to ride out silently: a stored
  // base address can point this console at a backend too old to have the
  // watch route at all, and then "keep the last face" keeps nothing —
  // the tab simply never appears, which reads as the feature being
  // gone. Unreachable is a state the tab shows, not one it hides in.
  const [unreachable, setUnreachable] = useState(false);
  // Which row is elaborated, if any. Closes with the panel.
  const [which, setWhich] = useState<Tone | null>(null);

  const load = useCallback(() => {
    const { profileId, ownerToken } = session;
    if (!profileId || !ownerToken) return;
    api.watchFace(profileId, ownerToken)
      .then((f) => { setFace(f); setUnreachable(false); })
      .catch(() => { setUnreachable(true); /* keep any last face */ });
  }, [session.profileId, session.ownerToken]);

  useEffect(() => {
    load();
    const timer = setInterval(load, POLL_MS);
    return () => clearInterval(timer);
  }, [load]);

  useEffect(() => { if (!open) setWhich(null); }, [open]);

  if (!face) {
    if (!unreachable || !session.profileId) return null;
    return (
      <button className="edge-tab wl-tab wl-dot-off" type="button"
              onClick={load}
              aria-label={tr("lights.unreachable", lang)}
              title={tr("lights.unreachable", lang)}>
        <span className="wl-glyph" aria-hidden="true">🚦</span>
        <span className="edge-tab-word">{tr("dock.lights", lang)}</span>
      </button>
    );
  }
  const worstTone = worst(face);

  const rows: { tone: Tone; label: string; n: number }[] = [
    { tone: "green", label: "working", n: face.summary.working },
    { tone: "amber", label: "needs a hand", n: face.summary.needing_assistance },
    { tone: "red", label: "stopped", n: face.summary.stopped },
  ];
  const names = which ? under(face, which) : [];

  return (
    <>
      <button className={"edge-tab wl-tab" + (open ? " on" : "")}
              type="button" aria-expanded={open} onClick={onToggle}
              aria-label={tr("dock.lights", lang)}
              title={tr("dock.lights", lang)}
              style={{ borderColor: COLORS[worstTone] }}>
        <span className="wl-glyph" aria-hidden="true">🚦</span>
        <span className="edge-tab-word">{tr("dock.lights", lang)}</span>
      </button>
      {open && (
        <div className={"edge-panel watch-lights" + (which ? " elaborated" : "")}
             role="status" aria-label={tr("dock.lights", lang)}
             style={{ borderColor: COLORS[worstTone] }}>
          <div className="wl-head">
            <span className="wl-name">{face.chip.display_name}</span>
          </div>
          {rows.map((r) => (
            <div key={r.label} className="wl-group">
              <button type="button"
                      className={"wl-row" + (which === r.tone ? " on" : "")}
                      aria-expanded={which === r.tone}
                      title={tr("lights.which", lang)}
                      onClick={() => setWhich(which === r.tone ? null : r.tone)}>
                <span className="wl-light" style={{ background: COLORS[r.tone] }} />
                <span className="wl-count">{r.n}</span>
                <span className="wl-label">{r.label}</span>
              </button>
              {which === r.tone && (
                <ul className="wl-who">
                  {names.length
                    ? names.map((name, i) => <li key={i}>{name}</li>)
                    : <li className="wl-none">{tr("lights.nobody", lang)}</li>}
                </ul>
              )}
            </div>
          ))}
          <div className="wl-foot">
            {face.chip.pending_approvals > 0
              ? `${face.chip.pending_approvals} approval${face.chip.pending_approvals === 1 ? "" : "s"} waiting`
              : "all quiet"}
          </div>
        </div>
      )}
    </>
  );
}
