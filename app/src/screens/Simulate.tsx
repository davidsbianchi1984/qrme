import { useEffect, useState } from "react";
import { api, SimulationOut } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// Real-time simulation (spec clauses 1 & 5): ask the profile what the person
// it represents would likely decide and do. Owner-only, and honest about two
// things the screen must not soften: the narrative is a watermarked
// prediction, never the person's word, and the confidence number is earned
// from real evidence — it is shown WITH its basis so nobody reads fluency
// as certainty.
const HORIZONS = [
  { id: "immediate", key: "sim.h.immediate" },
  { id: "short_term", key: "sim.h.short_term" },
  { id: "long_term", key: "sim.h.long_term" },
] as const;

export function Simulate({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [scenario, setScenario] = useState("");
  const [horizon, setHorizon] = useState<(typeof HORIZONS)[number]["id"]>("short_term");
  const [runs, setRuns] = useState<SimulationOut[]>([]);
  const [latest, setLatest] = useState<SimulationOut | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  function load() {
    if (!session.profileId || !session.ownerToken) return;
    api.simulations(session.profileId, session.ownerToken)
      .then(setRuns).catch(() => setRuns([]));
  }
  useEffect(load, [session.profileId, session.ownerToken]);

  if (!session.profileId || !session.ownerToken) {
    return <div className="screen">
      <p className="muted center">{tr("sim.owneronly", lang)}</p>
    </div>;
  }

  async function run() {
    if (!scenario.trim()) { setError(tr("sim.describe", lang)); return; }
    setBusy(true); setError(null);
    try {
      const out = await api.simulate(session.profileId!, {
        scenario: scenario.trim(), horizon,
        interactor_id: session.interactorId || undefined,
      }, session.ownerToken!);
      setLatest(out);
      setScenario("");
      load();
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  // One sentence with three holes rather than four fragments: the number
  // does not lead the clause in Japanese and the two counts swap places.
  const confidenceNote = (s: SimulationOut) =>
    tr("sim.confidence", lang)
      .replace("{score}", s.confidence.toFixed(2))
      .replace("{items}", String(s.basis.source_items))
      .replace("{turns}", String(s.basis.remembered_turns));

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("sim.title", lang)}</h2>
        <span className="muted small">{tr("sim.pitch", lang)}</span>
      </header>

      <div className="card">
        <h3>
          {fill(tr("sim.runof", lang),
                { name: session.profile?.display_name })}
        </h3>
        <label>{tr("sim.scenario", lang)}
          <textarea value={scenario} rows={3}
                    placeholder={tr("sim.scenario.ph", lang)}
                    onChange={(e) => setScenario(e.target.value)} />
        </label>
        <div className="row">
          <label>{tr("sim.horizon", lang)}
            <select value={horizon} onChange={(e) => setHorizon(e.target.value as typeof horizon)}>
              {HORIZONS.map((h) => (
                <option key={h.id} value={h.id}>{tr(h.key, lang)}</option>
              ))}
            </select>
          </label>
          <button className="primary" disabled={busy} onClick={run}>
            {busy ? tr("sim.modeling", lang) : tr("sim.run", lang)}
          </button>
        </div>
      </div>

      {latest && (
        <div className="card">
          <h3>{tr("sim.prediction", lang)}</h3>
          <p style={{ whiteSpace: "pre-wrap" }}>{latest.narrative}</p>
          <p className="muted small">{confidenceNote(latest)}</p>
          <p className="muted small">{latest.disclaimer}</p>
        </div>
      )}

      {runs.length > 0 && (
        <div className="card">
          <h3>{tr("sim.pastruns", lang)}</h3>
          {runs.slice().reverse().map((s) => (
            <div key={s.id} className="friend-row">
              <span className="tag">{s.confidence.toFixed(2)}</span>
              <b>{s.scenario.length > 60 ? s.scenario.slice(0, 60) + "…" : s.scenario}</b>
              <span className="muted small">{s.horizon.replace("_", " ")}</span>
            </div>
          ))}
        </div>
      )}

      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
