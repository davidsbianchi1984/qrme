import { useEffect, useState, type ReactNode } from "react";
import { api, type HandAction, type HandGrant, type HandsVocabulary,
         type Reach, type Routine } from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The hands.
 *
 * The profiles could see and speak; this is the screen where one is given
 * permission to press a button on somebody's machine. Which means the
 * design problem is not *how do I start it* — that is one button — it is
 * **how does a person see, at a glance, exactly what they just handed
 * over, and take it back in one press**.
 *
 * So the screen is built around the grant rather than around the errand:
 *
 * - the bounds are shown as bounds. Places, moves, minutes and steps are
 *   four fields on one card because they are four halves of one sentence,
 *   and a screen that buried the step budget under "advanced" would be
 *   drawing the dangerous part as the boring part;
 * - **both doors are on the same card.** The owner picks the permission
 *   from the list, or types what they would have said out loud, and the
 *   row that comes back is rendered identically either way. A spoken
 *   grant that reads differently from a picked one invites the belief
 *   that it *is* different;
 * - the told box echoes what the words were understood to mean. Somebody
 *   who says "you can click and type in my calendar for the next hour"
 *   should see `calendar · press, type · 60 minutes` come back, and the
 *   moment that echo is wrong they know before anything moves;
 * - **the ledger shows refusals.** A hand that declined to type a
 *   password is the most reassuring row on the screen and the easiest one
 *   to hide, so refused steps are drawn in line with the rest and carry
 *   their reason;
 * - `never` is rendered from the server, verbatim, above everything. It
 *   names the iPhone case out loud — Apple provides no way for anything
 *   to drive another app's interface — because a person whose phone did
 *   nothing deserves the reason and not a spinner.
 *
 * `Take back` is the loudest control here and never refuses: a reach
 * already running stops at its next step, because the check lives in the
 * backend's `act`, not in this button.
 */
export function Hands() {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [vocab, setVocab] = useState<HandsVocabulary | null>(null);
  const [grants, setGrants] = useState<HandGrant[]>([]);
  const [routines, setRoutines] = useState<Routine[]>([]);

  const [surface, setSurface] = useState("computer");
  const [places, setPlaces] = useState("");
  const [verbs, setVerbs] = useState<string[]>(["press", "type"]);
  const [minutes, setMinutes] = useState(30);
  const [steps, setSteps] = useState(40);
  const [watched, setWatched] = useState(true);
  const [said, setSaid] = useState("");

  const [useGrant, setUseGrant] = useState("");
  const [errand, setErrand] = useState("");
  const [platform, setPlatform] = useState("macos");
  const [mode, setMode] = useState("acting");

  const [reach, setReach] = useState<Reach | null>(null);
  const [ledger, setLedger] = useState<HandAction[]>([]);
  const [routineName, setRoutineName] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<ReactNode>(null);
  const fail = (e: unknown) => setError(e);

  useEffect(() => {
    api.handsVocabulary().then(setVocab).catch(() => setVocab(null));
  }, []);

  function load() {
    if (!me || !token) { setGrants([]); setRoutines([]); return; }
    api.handGrants(me, token).then((r) => setGrants(r.grants))
      .catch(() => setGrants([]));
    api.routines(me, token).then((r) => setRoutines(r.routines))
      .catch(() => setRoutines([]));
  }
  useEffect(load, [me, token]);

  function refresh(id: string) {
    api.readReach(me, token, id).then((r) => {
      setReach(r.reach); setLedger(r.ledger);
    }).catch(fail);
  }

  const live = grants.filter((g) => g.live);
  // An iPhone is on the list of platforms and not on the list of drivable
  // ones. Saying so here, beside the picker, is the difference between a
  // decision and a bug — the backend refuses either way.
  const undrivable = !!vocab && mode === "acting"
    && !vocab.drivable.includes(platform);

  function toggleVerb(v: string) {
    setVerbs((prev) => prev.includes(v)
      ? prev.filter((x) => x !== v) : [...prev, v]);
  }

  async function give() {
    setError(null); setNote(null);
    try {
      const written = await api.grantHands(me, token, {
        surface,
        places: places.split(",").map((p) => p.trim()).filter(Boolean),
        verbs, minutes, steps, watched,
      });
      setNote(fill(tr("hnd.gave", lang), { places: written.places.join(", ") }));
      setUseGrant(written.id);
      load();
    } catch (e) { fail(e); }
  }

  async function tell() {
    setError(null); setNote(null);
    try {
      const written = await api.tellHands(me, token,
                                          { said, surface, watched });
      setNote(fill(tr("hnd.heard", lang), {
        places: written.places.join(", "),
        verbs: written.verbs.join(", "),
      }));
      setSaid(""); setUseGrant(written.id); load();
    } catch (e) { fail(e); }
  }

  async function takeBack(id: string) {
    setError(null); setNote(null);
    try {
      await api.takeHandsBack(me, token, id);
      setNote(tr("hnd.tookback", lang));
      load();
    } catch (e) { fail(e); }
  }

  async function begin() {
    setError(null); setNote(null);
    try {
      const opened = await api.openReach(me, token, {
        grant_id: useGrant, errand, platform, mode,
      });
      setReach(opened); setLedger([]);
    } catch (e) { fail(e); }
  }

  async function stop() {
    if (!reach) return;
    setError(null);
    try {
      const ended = await api.stopReach(me, token, reach.id);
      setReach(ended);
    } catch (e) { fail(e); }
  }

  async function writeItDown() {
    if (!reach) return;
    setError(null); setNote(null);
    try {
      await api.routineFromReach(me, token,
                                 { reach_id: reach.id, name: routineName });
      setNote(tr("hnd.wrotedown", lang));
      setRoutineName(""); load();
    } catch (e) { fail(e); }
  }

  async function again(routineId: string) {
    setError(null); setNote(null);
    try {
      const run = await api.replayRoutine(me, token, routineId,
                                          { grant_id: useGrant, platform });
      setReach(run.reach);
      refresh(run.reach.id);
      load();
    } catch (e) { fail(e); }
  }

  return (
    <div className="screen" id="hands">
      <h2>{tr("hnd.title", lang)}</h2>
      <p className="muted">{tr("hnd.pitch", lang)}</p>

      {/* The refusals, from the server, above everything else. */}
      {vocab && (
        <div className="card">
          <h3>{tr("hnd.never", lang)}</h3>
          <ul className="small">
            {vocab.never.map((line) => <li key={line}>{line}</li>)}
          </ul>
        </div>
      )}

      <Refusal error={error} />
      {note && <p className="small">{note}</p>}

      <div className="card">
        <h3>{tr("hnd.give", lang)}</h3>
        <p className="muted small">{tr("hnd.give.pitch", lang)}</p>

        <div className="row">
          <label>{tr("hnd.surface", lang)}
            <select value={surface}
                    onChange={(e) => setSurface(e.target.value)}>
              {(vocab?.surfaces || ["computer"]).map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
          <label>{tr("hnd.places", lang)}
            <input value={places} onChange={(e) => setPlaces(e.target.value)}
                   placeholder={tr("hnd.places.hint", lang)} />
          </label>
        </div>

        <p className="small">{tr("hnd.moves", lang)}</p>
        <div className="row">
          {(vocab?.verbs || []).map((v) => (
            <label key={v} className="small">
              <input type="checkbox" checked={verbs.includes(v)}
                     disabled={["look", "ask", "done"].includes(v)}
                     onChange={() => toggleVerb(v)} /> {v}
            </label>
          ))}
        </div>

        <div className="row">
          <label>{tr("hnd.minutes", lang)}
            <input type="number" min={1} max={vocab?.caps.minutes || 240}
                   value={minutes}
                   onChange={(e) => setMinutes(Number(e.target.value))} />
          </label>
          <label>{tr("hnd.steps", lang)}
            <input type="number" min={1} max={vocab?.caps.steps || 200}
                   value={steps}
                   onChange={(e) => setSteps(Number(e.target.value))} />
          </label>
          <label className="small">
            <input type="checkbox" checked={watched}
                   onChange={(e) => setWatched(e.target.checked)} />
            {" "}{tr("hnd.watched", lang)}
          </label>
          <button disabled={!me || !token || !places.trim() || !verbs.length}
                  onClick={give}>{tr("hnd.give.go", lang)}</button>
        </div>

        <hr />
        <p className="small">{tr("hnd.told", lang)}</p>
        <p className="muted small">{tr("hnd.told.pitch", lang)}</p>
        <div className="row">
          <input value={said} onChange={(e) => setSaid(e.target.value)}
                 placeholder={tr("hnd.told.hint", lang)} />
          <button disabled={!me || !token || !said.trim()}
                  onClick={tell}>{tr("hnd.told.go", lang)}</button>
        </div>
      </div>

      <div className="card">
        <h3>{tr("hnd.now", lang)}</h3>
        {!live.length && <p className="muted small">{tr("hnd.none", lang)}</p>}
        {grants.map((g) => (
          <div key={g.id} className="row">
            <span className="small">
              <strong>{g.places.join(", ")}</strong> · {g.verbs.join(", ")}
              {" · "}{g.steps} {tr("hnd.stepsword", lang)}
              {" · "}{g.door}
              {!g.live && ` · ${tr("hnd.over", lang)}`}
            </span>
            {g.said && <span className="muted small">“{g.said}”</span>}
            {g.live && (
              <button onClick={() => takeBack(g.id)}>
                {tr("hnd.takeback", lang)}
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("hnd.put", lang)}</h3>
        <div className="row">
          <select value={useGrant} onChange={(e) => setUseGrant(e.target.value)}>
            <option value="">{tr("hnd.pickgrant", lang)}</option>
            {live.map((g) => (
              <option key={g.id} value={g.id}>{g.places.join(", ")}</option>
            ))}
          </select>
          <select value={platform}
                  onChange={(e) => setPlatform(e.target.value)}>
            {(vocab?.platforms || ["macos"]).map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="acting">{tr("hnd.mode.act", lang)}</option>
            <option value="watching">{tr("hnd.mode.watch", lang)}</option>
          </select>
        </div>
        <div className="row">
          <input value={errand} onChange={(e) => setErrand(e.target.value)}
                 placeholder={tr("hnd.errand", lang)} />
          <button disabled={!useGrant || !errand.trim() || undrivable}
                  onClick={begin}>{tr("hnd.put.go", lang)}</button>
        </div>
        {undrivable && (
          <p className="small">{tr("hnd.undrivable", lang)}</p>
        )}
      </div>

      {reach && (
        <div className="card">
          <h3>{reach.errand}</h3>
          <p className="muted small">
            {fill(tr("hnd.reach.line", lang), {
              state: reach.state, left: reach.steps_left,
              where: reach.platform,
            })}
          </p>
          {reach.why && <p className="small">{reach.why}</p>}
          <div className="row">
            <button onClick={() => refresh(reach.id)}>
              {tr("hnd.refresh", lang)}
            </button>
            {reach.state === "open" && (
              <button onClick={stop}>{tr("hnd.stop", lang)}</button>
            )}
          </div>
          {ledger.map((step) => (
            <p key={step.n} className="small">
              <strong>{step.n}. {step.verb}</strong>
              {step.target ? ` — ${step.target}` : ""}
              {step.outcome !== "done" && ` · ${step.outcome}`}
              {step.note && <span className="muted"> {step.note}</span>}
              {step.saw && <span className="muted small"> · {step.saw}</span>}
            </p>
          ))}
          <div className="row">
            <input value={routineName}
                   onChange={(e) => setRoutineName(e.target.value)}
                   placeholder={tr("hnd.name", lang)} />
            <button disabled={!routineName.trim() || !ledger.length}
                    onClick={writeItDown}>{tr("hnd.write", lang)}</button>
          </div>
        </div>
      )}

      <div className="card">
        <h3>{tr("hnd.again", lang)}</h3>
        <p className="muted small">{tr("hnd.again.pitch", lang)}</p>
        {!routines.length && <p className="muted small">{tr("hnd.noroutines", lang)}</p>}
        {routines.map((r) => (
          <div key={r.id} className="row">
            <span className="small">
              <strong>{r.name}</strong> · {r.steps.length} · {r.learned}
              {r.runs ? ` · ${r.runs}` : ""}
            </span>
            <button disabled={!useGrant} onClick={() => again(r.id)}>
              {tr("hnd.again.go", lang)}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
