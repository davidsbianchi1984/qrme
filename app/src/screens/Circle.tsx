import { useEffect, useState } from "react";
import { api, getBase } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * Your circle — the friends you already have, as people rather than rows.
 *
 * The list existed twice and neither telling was this one. The Friends
 * screen is a workbench: the whole deployment pool, search, add, remove —
 * open it to *change* the list. Discover is a storefront: everybody,
 * described, with an offer on every card. "See all" from the homepage's
 * top-friends row first pointed at Discover, and the owner pulled it
 * back — "I don't think when a user wants to view his friends we should
 * be showing ones that aren't his friends and offering to add them."
 *
 *     asked     show me all my friends, and what they do
 *     mattered  the only screens that said what anybody does also
 *               offered strangers
 *
 * So: only friends, in the descriptive card style — the face, the blurb,
 * the tags — and no add button anywhere, because everybody here has
 * already been added. A face opens their homepage, same as everywhere.
 * The one door out is on the empty state, where Discover is exactly the
 * right answer.
 */
export function Circle({ onVisit, onMeet }: {
  /** Press a face and land on that person's homepage. */
  onVisit: (profileId: string) => void;
  /** Where an empty circle goes to stop being one. */
  onMeet: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  type Row = {
    profile_id: string; display_name: string; handle?: string | null;
    avatar?: string | null; avatar_kind?: string | null;
    verified: boolean; blurb?: string | null; tags: string[];
  };
  const [rows, setRows] = useState<Row[] | null>(null);

  useEffect(() => {
    if (!session.profileId) { setRows([]); return; }
    // The friends list carries names and faces; what each friend *does*
    // lives with the pool and the listings, so the three are read
    // together and joined on the friends — never the other way round.
    // The pool or the marketplace failing costs the descriptions, not
    // the circle: a friend with no listing is still a friend.
    Promise.all([
      api.friends(session.profileId),
      api.browsePeople().catch(
        () => ({ found: [], head_count: 0, kind_counts: {} } as
                 Awaited<ReturnType<typeof api.browsePeople>>)),
      api.marketplace().catch(
        () => [] as Awaited<ReturnType<typeof api.marketplace>>),
    ]).then(([mine, pool, listings]) => {
      const said = new Map(listings.map((l) => [l.profile_id, l]));
      const faces = new Map(pool.found.map((p) => [p.profile_id, p]));
      setRows(mine.friends.map((f) => {
        const l = said.get(f.profile_id);
        const p = faces.get(f.profile_id);
        return {
          profile_id: f.profile_id,
          display_name: f.display_name,
          handle: f.handle,
          avatar: f.avatar ?? p?.avatar ?? null,
          avatar_kind: l?.avatar_kind ?? p?.avatar_kind ?? null,
          verified: Boolean(
            (p?.verification as { verified?: boolean } | null)?.verified),
          blurb: l?.blurb ?? l?.purpose ?? null,
          tags: l?.tags ?? [],
        };
      }));
    }).catch(() => setRows([]));
  }, [session.profileId]);

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("crc.title", lang)}</h2>
        <span className="muted small">{tr("crc.pitch", lang)}</span>
      </header>

      {rows !== null && rows.length === 0 && (
        <div className="card">
          <p className="muted">{tr("crc.empty", lang)}</p>
          <button className="primary" onClick={onMeet}>
            {tr("crc.meet", lang)}
          </button>
        </div>
      )}

      <div className="discover-grid">
        {(rows ?? []).map((c) => (
          <div key={c.profile_id} className="card discover-card">
            <button className="dc-open" onClick={() => onVisit(c.profile_id)}
                    aria-label={c.display_name}>
              <div className="dc-face">
                {c.avatar ? (
                  <img className="dc-avatar" src={getBase() + c.avatar}
                       alt={c.display_name} />
                ) : (
                  <span className="dc-avatar dc-initials">
                    {c.display_name.split(/\s+/).map((w) => w[0]).join("")
                      .slice(0, 2)}
                  </span>
                )}
              </div>
              {c.avatar_kind === "ai" && (
                <span className="dc-badge ai">{tr("dsc.badge.ai", lang)}</span>
              )}
              {c.avatar_kind === "real_photo" && (
                <span className="dc-badge real">
                  {tr("dsc.badge.real", lang)}
                </span>
              )}
              {c.verified && (
                <span className="dc-badge verified">
                  {tr("dsc.badge.verified", lang)}
                </span>
              )}
              <b>{c.display_name}</b>
              {c.handle && (
                <span className="muted small">@{c.handle}</span>
              )}
            </button>
            {c.blurb && <p className="muted small">{c.blurb}</p>}
            <div className="tag-row">
              {c.tags.slice(0, 4).map((t) =>
                <span key={t} className="tag">{t}</span>)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
