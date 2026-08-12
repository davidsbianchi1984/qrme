import { useEffect, useState } from "react";
import { api, getBase, type Avatar, type ProfilePage, type Stats } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

export function Home({ go }: {
  go: (t: "chat" | "relationships" | "memory" | "blend" | "simulate"
        | "campaigns" | "org" | "plans" | "friends") => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [stats, setStats] = useState<Stats | null>(null);
  const [face, setFace] = useState<Avatar | null>(null);
  const [pals, setPals] = useState<
    Awaited<ReturnType<typeof api.friends>>["friends"]>([]);
  // The face you clicked, and their page as a visitor sees it. The field
  // report behind it: tapping a friend's picture went to the whole
  // friends list — a particular person's face led to a crowd.
  const [visiting, setVisiting] = useState<
    { name: string; avatar: string | null; page: ProfilePage } | null>(null);
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
              <button key={f.profile_id} onClick={() =>
                api.page(f.profile_id)
                  .then((page) => setVisiting(
                    { name: f.display_name, avatar: f.avatar ?? null, page }))
                  .catch(setError)}>
                {f.avatar ? (
                  <img className="presence-bubble" alt=""
                       src={f.avatar.startsWith("http")
                              ? f.avatar : getBase() + f.avatar} />
                ) : (
                  <div className="presence-bubble orbfill">
                    {f.display_name.slice(0, 1)}
                  </div>
                )}
                <span className="presence-name">{f.display_name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {visiting && (
        <div className="card friend-visit">
          <div className="friend-visit-head">
            {visiting.avatar ? (
              <img className="presence-bubble" alt=""
                   src={visiting.avatar.startsWith("http")
                          ? visiting.avatar : getBase() + visiting.avatar} />
            ) : (
              <div className="presence-bubble orbfill">
                {visiting.name.slice(0, 1)}
              </div>
            )}
            <div>
              <h3>{visiting.name}</h3>
              {visiting.page.tagline && (
                <p className="muted small">{visiting.page.tagline}</p>
              )}
            </div>
            <button className="ghost" onClick={() => setVisiting(null)}>
              {tr("hom.visit.close", lang)}
            </button>
          </div>
          {visiting.page.about && (
            <p className="small">{visiting.page.about}</p>
          )}
          {visiting.page.links.length > 0 && (
            <p className="muted small">
              {visiting.page.links.map((l) => (
                <a key={l.url} href={l.url} target="_blank" rel="noreferrer"
                   style={{ marginRight: 10 }}>{l.label || l.url}</a>
              ))}
            </p>
          )}
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
          testers never find them. */}
      <div className="card">
        <h3>{tr("hom.newinrelease", lang)}</h3>
        <div className="actions">
          <button onClick={() => go("blend")}>{tr("hom.blend", lang)}</button>
          <button onClick={() => go("simulate")}>{tr("hom.simulate", lang)}</button>
          <button onClick={() => go("campaigns")}>{tr("hom.money", lang)}</button>
          <button onClick={() => go("org")}>{tr("hom.departments", lang)}</button>
        </div>
      </div>
    </div>
  );
}
