import { useEffect, useState } from "react";
import { api } from "../api";
import { useSession } from "../store";

// The friends list, founder first — the backend pins David Bianchi and his
// synthetic profile at positions one and two on every list, by design; the
// console finally shows it.
export function Friends() {
  const { session } = useSession();
  const [data, setData] = useState<Awaited<ReturnType<typeof api.friends>> | null>(null);
  const [suggested, setSuggested] = useState<{ profile_id: string; display_name: string }[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function load() {
    if (!session.profileId) return;
    api.friends(session.profileId).then(setData).catch((e) => setError((e as Error).message));
    api.suggestedFriends(session.profileId).then((s) => {
      const list = Array.isArray(s) ? s : (s.suggestions || []);
      setSuggested(list as { profile_id: string; display_name: string }[]);
    }).catch(() => setSuggested([]));
  }
  useEffect(load, [session.profileId]);

  if (!session.profileId) return <div className="screen"><p className="muted center">Sign in first.</p></div>;

  async function add(profileId: string) {
    setBusy(true); setError(null);
    try {
      await api.addFriend(session.profileId!, profileId, session.ownerToken!);
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  const founderHandles = new Set(data?.founder_handles || []);

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Friends</h2>
        <span className="muted small">the founder stands first, on every list</span>
      </header>

      <div className="card">
        {(data?.friends || []).length === 0 && (
          <p className="muted center">Loading, or no friends yet — the founder appears the moment the starter collection is installed (Discover).</p>
        )}
        {(data?.friends || []).map((f, i) => {
          const isFounder = f.pinned || (f.handle != null && founderHandles.has(f.handle));
          return (
            <div key={f.profile_id} className={"friend-row" + (isFounder ? " founder" : "")}>
              <span className="friend-rank">{i + 1}</span>
              <b>{f.display_name}</b>
              {isFounder && <span className="tag founder-tag">founder</span>}
              {f.handle && <span className="muted small">@{f.handle}</span>}
            </div>
          );
        })}
      </div>

      {suggested.length > 0 && (
        <div className="card">
          <h3>Suggested</h3>
          {suggested.map((s) => (
            <div key={s.profile_id} className="friend-row">
              <b>{s.display_name}</b>
              <button className="primary" disabled={busy} onClick={() => add(s.profile_id)}>Add</button>
            </div>
          ))}
        </div>
      )}

      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
