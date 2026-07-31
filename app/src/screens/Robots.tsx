import { useEffect, useState } from "react";
import { api, type BoundRobot, type RobotCommandEntry, type RobotModel,
         type RobotRow, type RobotSkill, type RobotSteering } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * A body to speak through.
 *
 * The native shells already had the catalogue, the binding and a command
 * button. The web console had none of it, so the three routes that describe
 * what a body has *become* — how it is steered, what it has learned, and what
 * it has been told to do — had no caller anywhere.
 *
 * The thing to get right here is that **three list-shaped things have almost
 * the same name and mean different things**:
 *
 * - `robot.commands` — what this model of body accepts at all. This is what
 *   the buttons are built from;
 * - `GET /robots/{id}/commands` — the audit log of what it has been told to
 *   do. Owner-only, and the reason it exists is that a body in somebody's
 *   home should not be able to be sent somewhere with no record;
 * - `GET /robots/{id}/skills` — task modules installed from a pack, which
 *   **extend** the allowlist with new verbs.
 *
 * A screen written from the route names would put the log where the buttons
 * belong, and it would typecheck.
 *
 * Two more things shown rather than smoothed:
 *
 * - each skill's `procedure` is rendered verbatim, because every one of them
 *   names what the body will *not* do — "reminders only: never dispense",
 *   "companionship, not care, and never a substitute for human contact" — and
 *   that is the sentence somebody pointing a robot at a relative has to read;
 * - `behavior_profile` is drawn beside the dials. It is what the dials
 *   actually become in a body — pace turns into motion eagerness, autonomy
 *   into initiative, assertiveness into firmness — and it is the difference
 *   between a slider and an explanation.
 *
 * Steering is Pro. That refusal now renders as an offer with a button.
 */
export function Robots({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [catalogue, setCatalogue] = useState<RobotModel[]>([]);
  const [rows, setRows] = useState<RobotRow[]>([]);
  const [bound, setBound] = useState<BoundRobot | null>(null);

  const [name, setName] = useState("");
  const [model, setModel] = useState("");

  const [open, setOpen] = useState<string>("");
  const [steering, setSteering] = useState<RobotSteering | null>(null);
  const [skills, setSkills] = useState<RobotSkill[]>([]);
  const [log, setLog] = useState<RobotCommandEntry[]>([]);
  const [say, setSay] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const fail = (e: unknown) => setError(e);

  useEffect(() => {
    api.robotCatalogue().then((r) => setCatalogue(r.robots)).catch(fail);
  }, []);

  function loadRobots() {
    if (!me || !token) { setRows([]); return; }
    api.robots(me, token).then(setRows).catch(() => setRows([]));
  }
  useEffect(loadRobots, [me, token]);

  function loadBody(id: string) {
    setOpen(id); setError(null);
    api.robotSteering(id, token).then(setSteering).catch(() => setSteering(null));
    api.robotSkills(id, token).then(setSkills).catch(() => setSkills([]));
    api.robotCommandLog(id, token).then(setLog).catch(() => setLog([]));
  }

  const chosen = rows.find((r) => r.id === open) || null;

  async function bind() {
    setError(null); setNote(null);
    try {
      const r = await api.bindRobot(me, { name: name.trim(), model }, token);
      setBound(r); setName(""); loadRobots();
    } catch (e) { fail(e); }
  }

  async function send(command: string, arg?: string) {
    setError(null); setNote(null);
    try {
      const r = await api.commandRobot(open, { command, arg }, token);
      setNote(r.said ? `“${r.said}”` : `${r.action} — ${r.status}.`);
      api.robotCommandLog(open, token).then(setLog).catch(() => undefined);
    } catch (e) { fail(e); }
  }

  async function steer(dial: string, value: number) {
    setError(null); setNote(null);
    try {
      const r = await api.setRobotSteering(open, { [dial]: value }, token);
      setSteering((s) => s && { ...s, values: r.values,
                                behavior_profile: r.behavior_profile });
    } catch (e) { fail(e); }
  }

  async function unbind(id: string) {
    setError(null); setNote(null);
    try {
      await api.unbindRobot(id, token);
      setNote("Unbound. The body is no longer this profile's to speak "
              + "through; nothing about the profile changed.");
      if (open === id) { setOpen(""); setSteering(null); }
      loadRobots();
    } catch (e) { fail(e); }
  }

  return (
    <div className="screen">
      <h2>Bodies</h2>
      <p className="muted small">
        A profile can speak through a robot. The personality, the memory and
        the voice are the same ones — only the form of expression changes.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Bind a body</h3>
        <div className="row">
          <input value={name} onChange={(e) => setName(e.target.value)}
                 placeholder="what you call it" style={{ flex: 1 }} />
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            <option value="">pick a model</option>
            {catalogue.map((m) => (
              <option key={m.model} value={m.model}>
                {m.label} · {m.maker}
              </option>
            ))}
          </select>
          <button disabled={!me || !token || !name.trim() || !model}
                  onClick={bind}>Bind</button>
        </div>
        {model && (() => {
          const m = catalogue.find((c) => c.model === model);
          return m ? (
            <p className="muted small">
              {m.kind.replace(/_/g, " ")} — {m.capabilities.join(", ")}
              {!m.llm_capable && " · cannot speak in character"}
            </p>
          ) : null;
        })()}
      </div>

      {bound && (
        <div className="card">
          <h3>{bound.name} — {bound.label}</h3>
          {/* The identity guarantee, verbatim. It is the claim the whole
              feature rests on, and it is the backend's sentence. */}
          <p className="small">{bound.identity.guarantee}</p>
          <p className="muted small">
            Invariant across {bound.identity.invariant_across}.
          </p>
          <p className="muted small">{bound.note}</p>
        </div>
      )}

      <div className="card">
        <h3>Bound bodies</h3>
        {rows.length === 0 && (
          <p className="muted small">
            {me && token ? "Nothing bound yet." : "Sign in as an owner."}
          </p>
        )}
        {rows.map((r) => (
          <div className="row" key={r.id}>
            <div style={{ flex: 1 }}>
              <strong>{r.name}</strong>
              <div className="muted small">
                {r.model} · {r.status} · bound {r.created_at.slice(0, 10)}
              </div>
            </div>
            <button onClick={() => loadBody(r.id)}>Open</button>
            {/* Named for what the response says — `unbound: true` — rather
                than for the HTTP verb. "Delete my robot" and "stop this
                profile speaking through it" are worth not confusing. */}
            <button onClick={() => unbind(r.id)}>Unbind</button>
          </div>
        ))}
      </div>

      {chosen && (
        <>
          <div className="card">
            <h3>Tell it to do something</h3>
            <p className="muted small">
              What this body accepts. Not everything a robot can be told —
              what <em>this model</em> is permitted, plus any task modules it
              has learned.
            </p>
            <div className="row">
              {chosen.commands.filter((c) => c !== "say").map((c) => (
                <button key={c} className="chip" onClick={() => send(c)}>
                  {c.replace(/_/g, " ")}
                </button>
              ))}
              {skills.map((s) => (
                <button key={s.task} className="chip"
                        onClick={() => send(s.task)}>
                  {s.title}
                </button>
              ))}
            </div>
            {chosen.commands.includes("say") && (
              <div className="row">
                <input value={say} onChange={(e) => setSay(e.target.value)}
                       placeholder="say something about…"
                       style={{ flex: 1 }} />
                <button disabled={!say.trim()}
                        onClick={() => { send("say", say.trim()); setSay(""); }}>
                  Say it
                </button>
              </div>
            )}
          </div>

          <div className="card">
            <h3>What it has learned</h3>
            {skills.length === 0 && (
              <p className="muted small">
                No task modules installed. A robot pack adds verbs to the list
                above, checked against what this body can physically do.
              </p>
            )}
            {skills.map((s) => (
              <div key={s.task}>
                <h4>{s.title}</h4>
                {/* Verbatim, always. Every procedure names what the body
                    will not do, and that limit is the part that matters to
                    whoever is in the room with it. */}
                <p className="small">{s.procedure}</p>
                <p className="muted small">from {s.pack_title}</p>
              </div>
            ))}
          </div>

          {steering && (
            <div className="card">
              <h3>How it comes across</h3>
              <p className="muted small">
                Steering shapes manner, not permissions. It never touches
                identity, boundaries, age-gating or what the body may be told
                to do.
              </p>
              {steering.dials.map((d) => (
                <div key={d.name}>
                  <label className="small">
                    {d.label} — {steering.values[d.name] ?? d.default}
                  </label>
                  <input type="range" min={d.min} max={d.max}
                         value={steering.values[d.name] ?? d.default}
                         onChange={(e) => steer(d.name, Number(e.target.value))} />
                  <div className="muted small">{d.low} → {d.high}</div>
                </div>
              ))}
              <h4>What that becomes in a body</h4>
              <p className="muted small">
                {Object.entries(steering.behavior_profile)
                  .map(([k, v]) => `${k.replace(/_/g, " ")} ${v}`)
                  .join(" · ")}
              </p>
            </div>
          )}

          <div className="card">
            <h3>Everything it has been told</h3>
            <p className="muted small">
              Owner-only, and kept for the obvious reason: a body in somebody's
              home should not be able to be sent anywhere with no record.
            </p>
            {log.length === 0 && <p className="muted small">Nothing yet.</p>}
            {log.map((c) => (
              <div className="row" key={c.id}>
                <div style={{ flex: 1 }}>
                  <strong>{c.command.replace(/_/g, " ")}</strong>
                  {c.arg && <> — {c.arg}</>}
                </div>
                <span className="muted small">
                  {c.created_at.replace("T", " ").slice(0, 16)}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
