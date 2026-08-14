import { useEffect, useState } from "react";
import { api, getBase, type Avatar, type Stats } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

export function Home({ go, onVisit }: {
  go: (t: "chat" | "relationships" | "memory" | "blend" | "simulate"
        | "campaigns" | "org" | "plans" | "friends"
        | "identity" | "stranger" | "rooms" | "studio") => void;
  /** Press a face and land on that person's homepage. */
  onVisit: (profileId: string) => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [stats, setStats] = useState<Stats | null>(null);
  const [face, setFace] = useState<Avatar | null>(null);
  const [pals, setPals] = useState<
    Awaited<ReturnType<typeof api.friends>>["friends"]>([]);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    if (!session.profileId || !session.ownerToken) return;
    api
      .stats(session.profileId, session.ownerToken)
      .then(setStats)
      .catch(setError);
    // The hero shows the profile's actual portrait; the orb is only the
    // fallback for a profile that has none yet.
    api.avatar(session.profileId, session.ownerToken)
      .then(setFace).catch(() => setFace(null));
    // The top of the friends list belongs on the front page — the founder
    // pins first, then the oldest friendships, as faces not rows.
    api.friends(session.profileId)
      .then((r) => setPals(r.friends.slice(0, 6))).catch(() => setPals([]));
  }, [session.profileId, session.ownerToken]);

  const p = session.profile;
  const tiles = [
    {
      key: "hom.tile.memory",
      value: stats ? String(stats.memory_entries) : "—",
      subKey: "hom.tile.entries",
    },
    {
      key: "hom.relationships",
      value: stats ? String(stats.relationship_graph) : "—",
      subKey: "hom.tile.connections",
    },
    {
      key: "hom.tile.engagement",
      value: stats?.engagement_avg != null
        ? `${Math.round(stats.engagement_avg * 100)}%` : "—",
      subKey: "hom.tile.average",
    },
    {
      key: "hom.tile.moderation",
      value: stats?.moderation_pass_rate != null
        ? `${(stats.moderation_pass_rate * 100).toFixed(1)}%` : "—",
      subKey: "hom.tile.passrate",
    },
  ];

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("hom.title", lang)}</h2>
        <span className="dot-online">{tr("hom.online", lang)}</span>
      </header>

      <div className="profile-hero">
        {face && face.asset && !face.placeholder ? (
          <img className="hero-face" alt=""
               src={face.asset.startsWith("http")
                      ? face.asset : getBase() + face.asset} />
        ) : (
          <div className="orb big" />
        )}
        <div>
          <h3>{p?.display_name}</h3>
          <div className="muted">
            {fill(tr("hom.aiversion", lang), { what: p?.purpose || p?.kind })}
          </div>
        </div>
      </div>

      <Refusal error={error} onPlans={() => go("plans")} variant="inline" />

      {pals.length > 0 && (
        <div className="top-friends">
          {/* The label is the door to the whole list; a face is the door
              to that person. */}
          <button className="tile-label linkish" onClick={() => go("friends")}>
            {tr("hom.friends", lang)}
          </button>
          <div className="friends-row">
            {pals.map((f) => (
              // Their homepage, not a card about them. What stood here read
              // their name and tagline into a panel and then drew the
              // signed-in profile's own tiles, persona and chat button
              // underneath — four different faces, four identical screens.
              // See screens/Profile.tsx for why no stats row followed them
              // over.
              <button key={f.profile_id}
                      onClick={() => onVisit(f.profile_id)}>
                {f.avatar ? (
                  <img className="presence-bubble" alt=""
                       src={f.avatar.startsWith("http")
                              ? f.avatar : getBase() + f.avatar} />
                ) : null}
                <span className="presence-name">{f.display_name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="tiles">
        {tiles.map((t) => (
          <div className="tile" key={t.key}>
            <div className="tile-label">{tr(t.key, lang)}</div>
            <div className="tile-value">{t.value}</div>
            <div className="tile-sub">{tr(t.subKey, lang)}</div>
          </div>
        ))}
      </div>

      <div className="persona-card">
        <div className="tile-label">{tr("hom.persona", lang)}</div>
        <p>{p?.persona}</p>
      </div>

      <div className="actions">
        <button className="primary" onClick={() => go("chat")}>
          {fill(tr("hom.chatwith", lang), { name: p?.display_name })}
        </button>
        <button onClick={() => go("relationships")}>
          {tr("hom.relationships", lang)}
        </button>
        <button onClick={() => go("memory")}>{tr("hom.memoryvault", lang)}</button>
      </div>

      {/* The doors this release opened — the front page names them, or
          testers never find them. A field report noticed this list had
          quietly stopped being true ("I don't think I've seen what's new
          get updated"), which is the one failure a card with this heading
          cannot afford: refresh it with every release, or retire it. */}
      <div className="card">
        <h3>{tr("hom.newinrelease", lang)}</h3>
        <div className="actions">
          <button onClick={() => go("memory")}>{tr("hom.curate", lang)}</button>
          <button onClick={() => go("identity")}>{tr("hom.exportqr", lang)}</button>
          <button onClick={() => go("rooms")}>{tr("hom.roomscene", lang)}</button>
          <button onClick={() => go("stranger")}>{tr("hom.roulette", lang)}</button>
          <button onClick={() => go("studio")}>{tr("hom.studio", lang)}</button>
        </div>
      </div>
    </div>
  );
}
