import { useCallback, useEffect, useState } from "react";
import { api, type WatchFace } from "./api";
import { t as tr, visitorLang } from "./l10n";
import { useSession } from "./store";

/**
 * The agent task lights, always on screen — a little round window the size
 * of a watch face, because that is exactly what it is: the same glanceable
 * payload the wrist gets (GET /profiles/{id}/watch), pinned to the corner
 * of the studio so the owner never has to go looking for whether an agent
 * is working (green), waiting on them (amber), or stopped (red).
 *
 * Mounted in App outside the tab switch, like Help: "on every screen" is a
 * property of the shell. Counts and the profile chip only — the full agent
 * list stays on the screens that can carry it. Minimizes to a dot in the
 * worst light's color when it is in the way; the choice sticks.
 */

const POLL_MS = 15000;
const MIN_KEY = "qrme.lights.min";

const COLORS = { green: "#43e08a", amber: "#ffb84d", red: "#e0687a" };

function worst(face: WatchFace): keyof typeof COLORS {
  if (face.summary.stopped > 0 || face.chip.light === "red") return "red";
  if (face.summary.needing_assistance > 0) return "amber";
  return "green";
}

export function WatchLights() {
  const { session } = useSession();
  const [face, setFace] = useState<WatchFace | null>(null);
  // The first fetch failing is not a blip to ride out silently: a stored
  // base address can point this console at a backend too old to have the
  // watch route at all, and then "keep the last face" keeps nothing —
  // the widget simply never appears, which reads as the feature being
  // gone. Unreachable is a state the widget shows, not one it hides in.
  const [unreachable, setUnreachable] = useState(false);
  const [min, setMin] = useState(() => localStorage.getItem(MIN_KEY) === "1");

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

  if (!face) {
    if (!unreachable || !session.profileId) return null;
    return (
      <button className="wl-dot wl-dot-off"
              onClick={load}
              aria-label={tr("lights.unreachable", visitorLang())}
              title={tr("lights.unreachable", visitorLang())} />
    );
  }
  const tone = worst(face);

  const setMinimized = (v: boolean) => {
    setMin(v);
    if (v) localStorage.setItem(MIN_KEY, "1");
    else localStorage.removeItem(MIN_KEY);
  };

  if (min) {
    return (
      <button className="wl-dot" style={{ background: COLORS[tone] }}
              onClick={() => setMinimized(false)}
              aria-label="Show agent lights" title="Agent lights" />
    );
  }

  const rows = [
    { color: COLORS.green, label: "working", n: face.summary.working },
    { color: COLORS.amber, label: "needs a hand", n: face.summary.needing_assistance },
    { color: COLORS.red, label: "stopped", n: face.summary.stopped },
  ];

  return (
    <div className="watch-lights" role="status" aria-label="Agent lights"
         style={{ borderColor: COLORS[tone] }}>
      <div className="wl-head">
        <span className="wl-name">{face.chip.display_name}</span>
        <button className="wl-min" onClick={() => setMinimized(true)}
                aria-label="Minimize agent lights">–</button>
      </div>
      {rows.map((r) => (
        <div className="wl-row" key={r.label}>
          <span className="wl-light" style={{ background: r.color }} />
          <span className="wl-count">{r.n}</span>
          <span className="wl-label">{r.label}</span>
        </div>
      ))}
      <div className="wl-foot">
        {face.chip.pending_approvals > 0
          ? `${face.chip.pending_approvals} approval${face.chip.pending_approvals === 1 ? "" : "s"} waiting`
          : "all quiet"}
      </div>
    </div>
  );
}
