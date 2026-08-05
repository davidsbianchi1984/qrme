import { useEffect, useState } from "react";
import { api } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// Hybrid profiles (spec [0038]): several people blended into one persona —
// both grandparents at once, in the shares you choose. Candidates are your
// own signed-in profile plus everything on the marketplace, because those are
// exactly the profiles the backend will accept as sources; showing anything
// else would collect a 403 the form could have prevented.
interface Pick {
  profile_id: string;
  display_name: string;
  weight: number;
  aspect: string;
}

export function Blend({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session, setSession } = useSession();
  const lang = visitorLang();
  const [candidates, setCandidates] = useState<{ profile_id: string; display_name: string }[]>([]);
  const [picks, setPicks] = useState<Pick[]>([]);
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [made, setMade] = useState<Awaited<ReturnType<typeof api.createComposite>> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    api.marketplace().then((cards) => {
      const own = session.profileId && session.profile
        ? [{ profile_id: session.profileId, display_name: session.profile.display_name }]
        : [];
      const seen = new Set(own.map((o) => o.profile_id));
      setCandidates([...own, ...cards.filter((c) => !seen.has(c.profile_id))]);
    }).catch((e) => setError(e));
  }, [session.profileId, session.profile]);

  function toggle(c: { profile_id: string; display_name: string }) {
    setPicks((p) =>
      p.some((x) => x.profile_id === c.profile_id)
        ? p.filter((x) => x.profile_id !== c.profile_id)
        : [...p, { ...c, weight: 1, aspect: "" }],
    );
  }

  function setPick(id: string, patch: Partial<Pick>) {
    setPicks((p) => p.map((x) => (x.profile_id === id ? { ...x, ...patch } : x)));
  }

  const total = picks.reduce((s, p) => s + (p.weight || 0), 0);

  async function blend() {
    if (!session.accountId) { setError(tr("bld.signin", lang)); return; }
    if (picks.length < 2) { setError(tr("bld.picktwo", lang)); return; }
    if (!name.trim()) { setError(tr("bld.namethe", lang)); return; }
    if (!birthdate) { setError(tr("bld.birthdateverifies", lang)); return; }
    setBusy(true); setError(null);
    try {
      const out = await api.createComposite({
        owner_id: session.accountId,
        display_name: name.trim(),
        verification: { birthdate },
        sources: picks.map((p) => ({
          profile_id: p.profile_id,
          weight: p.weight || 1,
          aspect: p.aspect.trim() || undefined,
        })),
      });
      setMade(out);
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  function adopt() {
    if (!made) return;
    setSession({ profileId: made.id, ownerToken: made.owner_token, profile: made });
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("bld.title", lang)}</h2>
        <span className="muted small">{tr("bld.pitch", lang)}</span>
      </header>

      {!made && (
        <>
          <div className="card">
            <h3>{tr("bld.whatis", lang)}</h3>
            {/* The bolded clause sits mid-sentence, so the sentence is one
                row with that clause as a hole. Japanese puts the verb where
                English puts the object, and splitting at the <b> would have
                handed a translator "Blending" and " whose persona mixes". */}
            <p className="muted small">
              {fill(tr("bld.blending", lang),
                    { creates: <b>{tr("bld.creates", lang)}</b> })}
            </p>
          </div>
          <div className="card">
            <h3>{tr("bld.whocan", lang)}</h3>
            <p className="muted small">{tr("bld.sources", lang)}</p>
            {candidates.length === 0 && (
              <p className="muted center">{tr("bld.nothingyet", lang)}</p>
            )}
            {candidates.map((c) => {
              const pick = picks.find((x) => x.profile_id === c.profile_id);
              const pct = pick && total > 0 ? Math.round((pick.weight / total) * 100) : null;
              return (
                <div key={c.profile_id} className="friend-row">
                  <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <input type="checkbox" checked={!!pick} onChange={() => toggle(c)} />
                    <b>{c.display_name}</b>
                  </label>
                  {pick && (
                    <>
                      <label>{tr("bld.share", lang)}
                        <input type="number" min={1} max={9} value={pick.weight}
                               style={{ width: 56 }}
                               onChange={(e) => setPick(c.profile_id, { weight: Number(e.target.value) || 1 })} />
                      </label>
                      <label>{tr("bld.their.label", lang)}
                        <input value={pick.aspect} placeholder={tr("bld.aspect.ph", lang)}
                               onChange={(e) => setPick(c.profile_id, { aspect: e.target.value })} />
                      </label>
                      {pct !== null && <span className="tag">{pct}%</span>}
                    </>
                  )}
                </div>
              );
            })}
          </div>

          <div className="card">
            <h3>{tr("bld.theblend", lang)}</h3>
            <div className="row">
              <label>{tr("bld.name", lang)}<input value={name} placeholder={tr("bld.name.ph", lang)}
                                onChange={(e) => setName(e.target.value)} /></label>
              <label>{tr("bld.birthdate", lang)}<input type="date" value={birthdate}
                                          onChange={(e) => setBirthdate(e.target.value)} /></label>
              <button className="primary" disabled={busy || picks.length < 2} onClick={blend}>
                {busy ? tr("bld.blendingbtn", lang) : tr("bld.blendbtn", lang)}
              </button>
            </div>
          </div>
        </>
      )}

      {made && (
        <div className="card">
          <h3>{made.display_name}</h3>
          <p className="muted small">{tr("bld.hybrid", lang)}</p>
          {made.composition.map((s) => (
            <div key={s.source_profile_id} className="friend-row">
              <span className="tag">{Math.round(s.weight * 100)}%</span>
              <b>{s.display_name}</b>
              {s.aspect && (
                <span className="muted small">
                  {fill(tr("bld.their", lang), { aspect: s.aspect })}
                </span>
              )}
            </div>
          ))}
          <div className="row">
            <button className="primary" onClick={adopt}>{tr("bld.usenow", lang)}</button>
            <button onClick={() => { setMade(null); setPicks([]); setName(""); }}>
              {tr("bld.another", lang)}
            </button>
          </div>
        </div>
      )}

      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
