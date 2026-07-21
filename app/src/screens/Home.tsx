import { useEffect, useState } from "react";
import { api, type Stats } from "../api";
import { useSession } from "../store";

export function Home({ go }: { go: (t: "chat" | "relationships" | "memory") => void }) {
  const { session } = useSession();
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session.profileId || !session.ownerToken) return;
    api
      .stats(session.profileId, session.ownerToken)
      .then(setStats)
      .catch((e) => setError((e as Error).message));
  }, [session.profileId, session.ownerToken]);

  const p = session.profile;
  const tiles = [
    { label: "Memory", value: stats ? String(stats.memory_entries) : "—", sub: "entries" },
    { label: "Relationships", value: stats ? String(stats.relationship_graph) : "—", sub: "connections" },
    {
      label: "Engagement",
      value: stats?.engagement_average != null
        ? `${Math.round(stats.engagement_average * 100)}%` : "—",
      sub: "average",
    },
    {
      label: "Moderation",
      value: stats?.moderation_pass_rate != null
        ? `${(stats.moderation_pass_rate * 100).toFixed(1)}%` : "—",
      sub: "pass rate",
    },
  ];

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Home</h2>
        <span className="dot-online">● Online</span>
      </header>

      <div className="profile-hero">
        <div className="orb big" />
        <div>
          <h3>{p?.display_name}</h3>
          <div className="muted">AI Version — {p?.purpose || p?.kind}</div>
        </div>
      </div>

      {error && <div className="error">⚠ {error}</div>}

      <div className="tiles">
        {tiles.map((t) => (
          <div className="tile" key={t.label}>
            <div className="tile-label">{t.label}</div>
            <div className="tile-value">{t.value}</div>
            <div className="tile-sub">{t.sub}</div>
          </div>
        ))}
      </div>

      <div className="persona-card">
        <div className="tile-label">Persona</div>
        <p>{p?.persona}</p>
      </div>

      <div className="actions">
        <button className="primary" onClick={() => go("chat")}>Chat with {p?.display_name}</button>
        <button onClick={() => go("relationships")}>Relationships</button>
        <button onClick={() => go("memory")}>Memory Vault</button>
      </div>
    </div>
  );
}
