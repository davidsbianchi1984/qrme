import { useEffect, useState } from "react";
import { api, type BoundRobot, type ConnectorCatalogue, type InstalledPack,
         type PackRow, type RobotCatalogue, type RobotCommandEntry,
         type RobotModel, type RobotRow, type RobotSkill,
         type RobotSteering } from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr, visitorLang } from "../l10n";
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
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [catalogue, setCatalogue] = useState<RobotModel[]>([]);
  const [market, setMarket] = useState<RobotCatalogue | null>(null);
  const [shelf, setShelf] = useState<PackRow[]>([]);
  const [fitted, setFitted] = useState<InstalledPack[]>([]);
  const [connectors, setConnectors] = useState<ConnectorCatalogue | null>(null);
  const [showAll, setShowAll] = useState(false);
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

  /** Run something, say what happened, and reload what it changed. The same
   *  shape the other screens use — kept here rather than shared because the
   *  reload each screen needs is the part that differs. */
  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null);
    try { await fn(); if (said) setNote(said); loadRobots(); }
    catch (e) { fail(e); }
  };

  useEffect(() => {
    api.robotCatalogue().then((r) => {
      setCatalogue(r.robots); setMarket(r);
    }).catch(fail);
    // Robot task packs specifically: a profile knowledge pack teaches a
    // persona, a robot pack teaches a body a verb, and fitting the wrong
    // kind is refused with a capability error rather than silently ignored.
    api.packs("robot").then(setShelf).catch(() => setShelf([]));
    api.connectorCatalogue().then(setConnectors).catch(() => setConnectors(null));
  }, []);

  function loadRobots() {
    if (!me || !token) { setRows([]); setFitted([]); return; }
    api.robots(me, token).then(setRows).catch(() => setRows([]));
    api.installedPacks(me, token).then(setFitted).catch(() => setFitted([]));
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
      <h2>{tr("rbt.title", lang)}</h2>
      <p className="muted small">{tr("rbt.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("rbt.bind", lang)}</h3>
        <div className="row">
          <input value={name} onChange={(e) => setName(e.target.value)}
                 placeholder={tr("rbt.bind.name.ph", lang)} style={{ flex: 1 }} />
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            <option value="">{tr("rbt.bind.pick", lang)}</option>
            {/* Grouped by whether you can actually get one. The announced
                group is listed on purpose and is not selectable — binding
                one answers 409 naming the status, and an option that only
                ever produces a refusal is worse than a disabled one. */}
            {["shipping", "preorder", "announced"].map((state) => {
              const group = catalogue.filter((m) => m.availability === state);
              if (group.length === 0) return null;
              return (
                <optgroup key={state} label={
                  state === "shipping" ? "On sale now"
                  : state === "preorder" ? "Open for pre-order"
                  : "Announced — not yet buyable"}>
                  {group.map((m) => (
                    <option key={m.model} value={m.model}
                            disabled={!m.bindable}>
                      {m.label} · {m.maker}
                    </option>
                  ))}
                </optgroup>
              );
            })}
          </select>
          <button disabled={!me || !token || !name.trim() || !model}
                  onClick={bind}>{tr("rbt.bind.go", lang)}</button>
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
            {fill(tr("rbt.invariant", lang),
              { across: bound.identity.invariant_across })}
          </p>
          <p className="muted small">{bound.note}</p>
        </div>
      )}

      <div className="card">
        <h3>{tr("rbt.market", lang)}</h3>
        {market && (
          <p className="muted small">
            {fill(tr("rbt.market.line", lang), {
              n: market.robots.length,
              m: Object.keys(market.by_maker).length,
              note: market.note,
              date: <strong>{market.reviewed}</strong>,
            })}
          </p>
        )}
        <div className="row">
          <button onClick={() => setShowAll((v) => !v)}>
            {showAll ? "Hide the full list" : "Show the full list"}
          </button>
        </div>
        {showAll && market && Object.entries(market.by_kind).map(([kind, list]) => (
          <div key={kind}>
            <h4>{kind.replace(/_/g, " ")}</h4>
            {list.map((m) => (
              <p className="small" key={m.model}>
                <strong>{m.label}</strong> · {m.maker} ·{" "}
                <em>{m.availability}</em>
                {!m.bindable && " — cannot be bound yet"}
                <br />
                <span className="muted small">
                  {m.capabilities.join(", ")}
                  {!m.llm_capable && " · cannot speak in character"}
                </span>
              </p>
            ))}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("rbt.conn", lang)}</h3>
        <p className="muted small">{tr("rbt.conn.pitch", lang)}</p>

        <h4>{tr("rbt.conn.shelf", lang)}</h4>
        {shelf.length === 0 && (
          <p className="muted small">{tr("rbt.conn.shelf.none", lang)}</p>
        )}
        {shelf.map((k) => (
          <p className="small" key={k.id}>
            <strong>{k.title}</strong> · {k.industry} · {k.publisher}
            {k.price ? ` · ${k.price}` : " · free"}
            {" "}
            <button disabled={!me || !token || !open}
                    onClick={act(async () => {
                      await api.installPack(k.id, {
                        profile_id: me, robot_id: open,
                        accept_price: Boolean(k.price),
                      }, token);
                      if (open) {
                        api.robotSkills(open, token).then(setSkills)
                          .catch(() => undefined);
                      }
                    }, "Fitted.")}>
              {tr("rbt.conn.fit", lang)}
            </button>
          </p>
        ))}
        {!open && (
          <p className="muted small">{tr("rbt.conn.openfirst", lang)}</p>
        )}

        <h4>{tr("rbt.conn.fitted", lang)}</h4>
        {fitted.length === 0 && (
          <p className="muted small">{tr("rbt.conn.fitted.none", lang)}</p>
        )}
        {fitted.map((k) => (
          <p className="small" key={`${k.id}-${k.robot_id ?? "profile"}`}>
            <strong>{k.title}</strong> ·{" "}
            {k.robot_id ? `on body ${k.robot_id}` : "on the profile itself"} ·
            {" "}{k.installed_at}
            {" "}
            <button disabled={!token}
                    onClick={act(async () => {
                      if (k.robot_id) {
                        await api.uninstallRobotPack(k.robot_id, k.id, token);
                      } else {
                        await api.uninstallPack(me, k.id, token);
                      }
                      if (open) {
                        api.robotSkills(open, token).then(setSkills)
                          .catch(() => undefined);
                      }
                    }, "Removed. Its tasks stop being commandable now.")}>
              {tr("rbt.conn.remove", lang)}
            </button>
          </p>
        ))}

        <h4>{tr("rbt.conn.components", lang)}</h4>
        {connectors && (
          <p className="muted small">
            {fill(tr("rbt.conn.counts", lang), {
              apps: connectors.app_count,
              providers: connectors.provider_count,
            })}
          </p>
        )}
        {connectors?.providers.map((prov) => (
          <p className="small" key={prov.provider}>
            <strong>{prov.label}</strong>:{" "}
            {prov.apps.map((a) => a.label).join(", ")}
          </p>
        ))}
      </div>

      <div className="card">
        <h3>{tr("rbt.bound", lang)}</h3>
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
                {fill(tr("rbt.bound.line", lang), {
                  model: r.model, status: r.status,
                  date: r.created_at.slice(0, 10),
                })}
              </div>
            </div>
            <button onClick={() => loadBody(r.id)}>{tr("rbt.bound.open", lang)}</button>
            {/* Named for what the response says — `unbound: true` — rather
                than for the HTTP verb. "Delete my robot" and "stop this
                profile speaking through it" are worth not confusing. */}
            <button onClick={() => unbind(r.id)}>{tr("rbt.bound.unbind", lang)}</button>
          </div>
        ))}
      </div>

      {chosen && (
        <>
          <div className="card">
            <h3>{tr("rbt.tell", lang)}</h3>
            <p className="muted small">{tr("rbt.tell.pitch", lang)}</p>
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
                       placeholder={tr("rbt.tell.say.ph", lang)}
                       style={{ flex: 1 }} />
                <button disabled={!say.trim()}
                        onClick={() => { send("say", say.trim()); setSay(""); }}>
                  {tr("rbt.tell.say", lang)}
                </button>
              </div>
            )}
          </div>

          <div className="card">
            <h3>{tr("rbt.learned", lang)}</h3>
            {skills.length === 0 && (
              <p className="muted small">{tr("rbt.learned.none", lang)}</p>
            )}
            {skills.map((s) => (
              <div key={s.task}>
                <h4>{s.title}</h4>
                {/* Verbatim, always. Every procedure names what the body
                    will not do, and that limit is the part that matters to
                    whoever is in the room with it. */}
                <p className="small">{s.procedure}</p>
                <p className="muted small">{fill(tr("rbt.learned.from", lang),
                  { pack: s.pack_title })}</p>
              </div>
            ))}
          </div>

          {steering && (
            <div className="card">
              <h3>{tr("rbt.steer", lang)}</h3>
              <p className="muted small">{tr("rbt.steer.pitch", lang)}</p>
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
              <h4>{tr("rbt.steer.becomes", lang)}</h4>
              <p className="muted small">
                {Object.entries(steering.behavior_profile)
                  .map(([k, v]) => `${k.replace(/_/g, " ")} ${v}`)
                  .join(" · ")}
              </p>
            </div>
          )}

          <div className="card">
            <h3>{tr("rbt.log", lang)}</h3>
            <p className="muted small">{tr("rbt.log.pitch", lang)}</p>
            {log.length === 0 && <p className="muted small">{tr("rbt.log.none", lang)}</p>}
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
