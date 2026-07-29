import { useEffect, useState } from "react";
import { api } from "../api";
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

export function Blend() {
  const { session, setSession } = useSession();
  const [candidates, setCandidates] = useState<{ profile_id: string; display_name: string }[]>([]);
  const [picks, setPicks] = useState<Pick[]>([]);
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [made, setMade] = useState<Awaited<ReturnType<typeof api.createComposite>> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.marketplace().then((cards) => {
      const own = session.profileId && session.profile
        ? [{ profile_id: session.profileId, display_name: session.profile.display_name }]
        : [];
      const seen = new Set(own.map((o) => o.profile_id));
      setCandidates([...own, ...cards.filter((c) => !seen.has(c.profile_id))]);
    }).catch((e) => setError((e as Error).message));
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
    if (!session.accountId) { setError("Sign in first."); return; }
    if (picks.length < 2) { setError("Pick at least two profiles to blend."); return; }
    if (!name.trim()) { setError("Name the blend."); return; }
    if (!birthdate) { setError("Your birthdate verifies you may create profiles."); return; }
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
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  function adopt() {
    if (!made) return;
    setSession({ profileId: made.id, ownerToken: made.owner_token, profile: made });
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Blend a Profile</h2>
        <span className="muted small">several people, one persona — and it says so openly</span>
      </header>

      {!made && (
        <>
          <div className="card">
            <h3>Who goes into the blend</h3>
            <p className="muted small">
              Your own profiles and anything listed on the marketplace. Rated
              profiles never blend; a profile that has departed still can —
              that is what this is for.
            </p>
            {candidates.length === 0 && (
              <p className="muted center">Nothing to blend yet — install the starter collection in Discover.</p>
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
                      <label>share
                        <input type="number" min={1} max={9} value={pick.weight}
                               style={{ width: 56 }}
                               onChange={(e) => setPick(c.profile_id, { weight: Number(e.target.value) || 1 })} />
                      </label>
                      <label>their…
                        <input value={pick.aspect} placeholder="e.g. storytelling"
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
            <h3>The blend</h3>
            <div className="row">
              <label>Name<input value={name} placeholder="e.g. The Grandfolks"
                                onChange={(e) => setName(e.target.value)} /></label>
              <label>Your birthdate<input type="date" value={birthdate}
                                          onChange={(e) => setBirthdate(e.target.value)} /></label>
              <button className="primary" disabled={busy || picks.length < 2} onClick={blend}>
                {busy ? "Blending…" : "Blend"}
              </button>
            </div>
          </div>
        </>
      )}

      {made && (
        <div className="card">
          <h3>{made.display_name}</h3>
          <p className="muted small">
            A hybrid profile. It will say openly that it is a blend and never
            claim to be any single one of its constituents.
          </p>
          {made.composition.map((s) => (
            <div key={s.source_profile_id} className="friend-row">
              <span className="tag">{Math.round(s.weight * 100)}%</span>
              <b>{s.display_name}</b>
              {s.aspect && <span className="muted small">their {s.aspect}</span>}
            </div>
          ))}
          <div className="row">
            <button className="primary" onClick={adopt}>Use this profile now</button>
            <button onClick={() => { setMade(null); setPicks([]); setName(""); }}>Blend another</button>
          </div>
        </div>
      )}

      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
