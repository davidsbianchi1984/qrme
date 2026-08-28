import { useEffect, useState } from "react";
import { api, type GrowthEntry, type RaiseDoors,
         type RaisedCharacter } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Raise — grow your own (docs/raise.md).
 *
 * "You begin with almost nothing — a temperament seed and a stage you
 * choose. Everything after that is made between you." This screen is the
 * creation door and the raising bench: the four preset doors (each just
 * a bundle of switches, reopenable below), the three temperament axes,
 * the character as they stand (stage, milestones, the cost of the next
 * door), the teach box where words and lessons land, and the Album —
 * the living timeline nothing ever edits.
 *
 * The characters a guardian holds are kept in this browser
 * (localStorage) the way a keyring is: the token IS the guardianship,
 * and the server never lists anybody's stable. Losing the browser loses
 * the keys, not the lives — the rows are all still there.
 */

type Held = { id: string; token: string; name: string };

function heldList(): Held[] {
  try {
    return JSON.parse(localStorage.getItem("qrme.raise.held") || "[]");
  } catch { return []; }
}

function hold(entry: Held) {
  try {
    const all = heldList().filter((h) => h.id !== entry.id);
    all.push(entry);
    localStorage.setItem("qrme.raise.held", JSON.stringify(all));
  } catch { /* a browser that keeps nothing still raises; it just forgets */ }
}

export function Raise({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const [doors, setDoors] = useState<RaiseDoors | null>(null);
  const [held, setHeld] = useState<Held[]>(heldList());
  const [open, setOpen] = useState<Held | null>(null);
  const [who, setWho] = useState<RaisedCharacter | null>(null);
  const [album, setAlbum] = useState<GrowthEntry[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // The creation form.
  const [name, setName] = useState("");
  const [stage, setStage] = useState("child");
  const [preset, setPreset] = useState("storybook");
  const [seed, setSeed] = useState<Record<string, number>>({});
  const [birthdate, setBirthdate] = useState("");
  const [terms, setTerms] = useState(false);

  // The teach box.
  const [teaching, setTeaching] = useState("word");
  const [what, setWhat] = useState("");

  useEffect(() => {
    api.raiseDoors().then(setDoors).catch(setError);
  }, []);

  useEffect(() => {
    if (!open) { setWho(null); setAlbum([]); return; }
    api.raiseCharacter(open.id, open.token).then(setWho).catch(setError);
    api.raiseAlbum(open.id, open.token)
      .then((r) => setAlbum(r.entries)).catch(() => setAlbum([]));
  }, [open]);

  async function begin() {
    if (!name.trim() || !birthdate || !terms) return;
    setBusy(true); setError(null); setNote(null);
    try {
      const made = await api.raiseBegin({
        // The signed-in account is the guardian — the same identity the
        // ordinary creation door uses, with the same desktop fallback.
        owner_id: session.accountId || "owner-desktop",
        display_name: name.trim(), stage, preset, temperament: seed,
        verification: { birthdate }, terms_consent: true,
      });
      const entry = { id: made.profile_id, token: made.owner_token,
                      name: made.display_name };
      hold(entry);
      setHeld(heldList());
      setOpen(entry);
      setName("");
      setNote(tr("raise.began", lang));
    } catch (e) { setError(e); } finally { setBusy(false); }
  }

  async function teach() {
    if (!open || !what.trim()) return;
    setBusy(true); setError(null); setNote(null);
    try {
      const r = await api.raiseTeach(open.id,
                                     { teaching, what: what.trim() },
                                     open.token);
      setWho(r.character);
      setWhat("");
      const back = await api.raiseAlbum(open.id, open.token);
      setAlbum(back.entries);
      if (r.stage_door) {
        // A door opened — said in the room's own voice, because an
        // earned stage is the biggest moment this screen has.
        setNote(tr("raise.dooropened", lang)
          .replace("{stage}", r.character.stage.replace("_", " ")));
      }
    } catch (e) { setError(e); } finally { setBusy(false); }
  }

  async function flip(switchName: string, value: unknown) {
    if (!open) return;
    setBusy(true); setError(null);
    try {
      const r = await api.raiseSwitches(open.id, { [switchName]: value },
                                        open.token);
      setWho((w) => (w ? { ...w, switches: r.switches } : w));
      // The mortality warning, said every time it turns on — the worded
      // warning is the law's half of the switch.
      if (r.warning) setNote(`⚠️ ${r.warning}`);
    } catch (e) { setError(e); } finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <h2>{tr("raise.title", lang)}</h2>
      <p className="muted small">{tr("raise.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {held.length > 0 && (
        <div className="card">
          <h3>{tr("raise.held", lang)}</h3>
          <div className="row" style={{ flexWrap: "wrap", gap: 8 }}>
            {held.map((h) => (
              <button key={h.id} className="chip"
                      aria-pressed={open?.id === h.id}
                      onClick={() => setOpen(h)}>
                🌱 {h.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {who && open && (
        <>
          <div className="card">
            <h3>{open.name} · {who.stage.replace("_", " ")}</h3>
            <p className="muted small">
              {tr("raise.entered", lang)
                .replace("{stage}", who.started_stage.replace("_", " "))
                .replace("{preset}", who.preset.replace("_", " "))}
            </p>
            <p className="small">
              {tr("raise.milestones", lang)
                .replace("{turns}", String(who.milestones.turns_together))
                .replace("{words}", String(who.milestones.words_taught))
                .replace("{lessons}", String(who.milestones.lessons_passed))}
            </p>
            {who.next_stage && (
              <p className="muted small">
                {tr("raise.nextdoor", lang)
                  .replace("{stage}", who.next_stage.replace("_", " "))
                  .replace("{at}", String(who.next_stage_at))
                  .replace("{points}", String(who.growth_points))}
              </p>
            )}
          </div>

          <div className="card">
            <h3>{tr("raise.teach", lang)}</h3>
            <p className="muted small">{tr("raise.teach.sub", lang)}</p>
            <div className="row">
              <select className="chip" value={teaching}
                      aria-label={tr("raise.teach.kind", lang)}
                      onChange={(e) => setTeaching(e.target.value)}>
                <option value="word">{tr("raise.teach.word", lang)}</option>
                <option value="lesson">{tr("raise.teach.lesson", lang)}</option>
                <option value="answer">{tr("raise.teach.answer", lang)}</option>
              </select>
              <input value={what} style={{ flex: 1 }}
                     placeholder={tr("raise.teach.ph", lang)}
                     onChange={(e) => setWhat(e.target.value)}
                     onKeyDown={(e) => e.key === "Enter" && void teach()} />
              <button className="primary" disabled={busy || !what.trim()}
                      onClick={() => void teach()}>
                {tr("raise.teach.go", lang)}
              </button>
            </div>
          </div>

          <div className="card">
            <h3>{tr("raise.switches", lang)}</h3>
            <p className="muted small">{tr("raise.switches.sub", lang)}</p>
            {Object.entries(who.switches).map(([k, v]) => (
              <div className="row" key={k}>
                <span className="small" style={{ flex: 1 }}>{k}</span>
                {typeof v === "boolean" ? (
                  <button className="chip" disabled={busy}
                          onClick={() => void flip(k, !v)}>
                    {v ? tr("raise.sw.on", lang) : tr("raise.sw.off", lang)}
                  </button>
                ) : (
                  <span className="muted small">{String(v)}</span>
                )}
              </div>
            ))}
          </div>

          <div className="card">
            <h3>{tr("raise.album", lang)}</h3>
            <p className="muted small">{tr("raise.album.sub", lang)}</p>
            {album.length === 0 && (
              <p className="muted small">{tr("raise.album.none", lang)}</p>
            )}
            {album.map((e) => (
              <p key={e.id} className="small">
                <span className="muted">{e.at.slice(0, 10)}</span>{" · "}
                {e.kind === "stage_door" ? "🚪 " : ""}{e.note}
              </p>
            ))}
          </div>
        </>
      )}

      <div className="card">
        <h3>{tr("raise.begin", lang)}</h3>
        <p className="muted small">{tr("raise.begin.sub", lang)}</p>
        <div className="row">
          <input value={name} style={{ flex: 1 }}
                 placeholder={tr("raise.name.ph", lang)}
                 onChange={(e) => setName(e.target.value)} />
          <select className="chip" value={stage}
                  aria-label={tr("raise.stage", lang)}
                  onChange={(e) => setStage(e.target.value)}>
            {(doors?.stages || []).map((st) => (
              <option key={st} value={st}>{st.replace("_", " ")}</option>
            ))}
          </select>
        </div>
        <div className="row" style={{ flexWrap: "wrap", gap: 8 }}>
          {Object.keys(doors?.presets || {}).map((p) => (
            <button key={p} className="chip" aria-pressed={preset === p}
                    onClick={() => setPreset(p)}>
              {tr(`raise.door.${p}`, lang)}
            </button>
          ))}
        </div>
        {(doors?.temperament_axes || []).map((axis) => {
          const [left, right] = axis.split("_");
          return (
            <div className="row" key={axis}>
              <span className="muted small">{left}</span>
              <input type="range" min={-100} max={100}
                     value={seed[axis] ?? 0} style={{ flex: 1 }}
                     aria-label={axis}
                     onChange={(e) => setSeed(
                       { ...seed, [axis]: Number(e.target.value) })} />
              <span className="muted small">{right}</span>
            </div>
          );
        })}
        <div className="row">
          <input type="date" value={birthdate}
                 aria-label={tr("raise.birthdate", lang)}
                 onChange={(e) => setBirthdate(e.target.value)} />
          <label className="small">
            <input type="checkbox" checked={terms}
                   onChange={(e) => setTerms(e.target.checked)} />{" "}
            {tr("raise.terms", lang)}
          </label>
          <button className="primary"
                  disabled={busy || !name.trim() || !birthdate || !terms}
                  onClick={() => void begin()}>
            {tr("raise.begin.go", lang)}
          </button>
        </div>
      </div>
    </div>
  );
}
