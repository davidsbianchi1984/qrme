import { useEffect, useState } from "react";
import { api, type MemoryEntry } from "../api";
import { useSession } from "../store";

export function Memory() {
  const { session } = useSession();
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    if (!session.profileId || !session.interactorId || !session.ownerToken) return;
    try {
      const data = await api.memory(
        session.profileId,
        session.interactorId,
        session.ownerToken,
      );
      const list = Array.isArray(data) ? data : data.history || [];
      setEntries(list);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, [session.profileId]);

  async function clear() {
    if (!session.profileId || !session.interactorId || !session.ownerToken) return;
    if (!confirm("Erase this conversation's memory? This cannot be undone.")) return;
    try {
      await api.clearMemory(session.profileId, session.interactorId, session.ownerToken);
      setEntries([]);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Memory Vault 🔒</h2>
        <span className="muted small">AES-256-GCM · stored in your vault</span>
      </header>

      {error && <div className="error">⚠ {error}</div>}

      <div className="memory-list">
        {entries.length === 0 && <div className="muted center">No memories yet — have a chat first.</div>}
        {entries.map((e, i) => (
          <div className={"mem " + e.role} key={i}>
            <span className="mem-role">{e.role}</span>
            <span className="mem-text">{e.content}</span>
          </div>
        ))}
      </div>

      {entries.length > 0 && (
        <div className="actions">
          <button onClick={load}>Refresh</button>
          <button className="danger" onClick={clear}>Delete this memory</button>
        </div>
      )}
    </div>
  );
}
