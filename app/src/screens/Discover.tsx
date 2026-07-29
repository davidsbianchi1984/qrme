import { useEffect, useState } from "react";
import { api } from "../api";
import { useSession } from "../store";

// For You + the marketplace + the starter collection, one discovery surface.
// Everything here was already in the backend; the console just never showed
// the doors. The starter collection installs on demand (idempotent server
// side), and every card is a real profile you can befriend.
export function Discover() {
  const { session } = useSession();
  const [cards, setCards] = useState<Awaited<ReturnType<typeof api.marketplace>>>([]);
  const [tag, setTag] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load(t?: string) {
    api.marketplace(t || undefined).then(setCards).catch((e) => setError((e as Error).message));
  }
  useEffect(() => load(), []);

  async function installStarters() {
    setBusy(true); setError(null); setNote(null);
    try {
      const r = await api.seedStarters();
      setNote(`Starter collection ready — ${r.created.length} new, ${r.skipped.length} already here.`);
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function befriend(profileId: string) {
    if (!session.profileId || !session.ownerToken) { setError("Sign in first."); return; }
    setBusy(true); setError(null);
    try {
      await api.addFriend(session.profileId, profileId, session.ownerToken);
      setNote("Added to your friends.");
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Discover</h2>
        <span className="muted small">the marketplace · every card is a real profile</span>
      </header>

      {cards.length === 0 && (
        <div className="card">
          <h3>Nothing listed yet</h3>
          <p className="muted small">
            The starter collection is 33 profiles across trades and
            interests, each carrying its industry's knowledge pack — one
            press to install, then talk to any of them.
          </p>
          <button className="primary" disabled={busy} onClick={installStarters}>
            {busy ? "Installing…" : "Install the starter collection"}
          </button>
        </div>
      )}

      {cards.length > 0 && (
        <div className="card">
          <div className="row">
            <label>Filter by tag
              <input value={tag} placeholder="e.g. music, carpentry"
                     onChange={(e) => setTag(e.target.value)} />
            </label>
            <button onClick={() => load(tag.trim())}>Search</button>
            <button disabled={busy} onClick={installStarters}>
              {busy ? "…" : "Refresh starters"}
            </button>
          </div>
        </div>
      )}

      <div className="discover-grid">
        {cards.map((c) => (
          <div key={c.profile_id} className="card discover-card">
            <b>{c.display_name}</b>
            {c.blurb && <p className="muted small">{c.blurb}</p>}
            <div className="tag-row">
              {c.tags.slice(0, 4).map((t) => <span key={t} className="tag">{t}</span>)}
            </div>
            <button className="primary" disabled={busy}
                    onClick={() => befriend(c.profile_id)}>Add friend</button>
          </div>
        ))}
      </div>

      {note && <div className="muted small">{note}</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
