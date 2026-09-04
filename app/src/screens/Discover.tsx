import { useEffect, useState } from "react";
import { api, getBase } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { Trade } from "../Trade";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// Everyone on this deployment, in one place.
//
// This screen used to render `GET /marketplace` alone — the opt-IN listing a
// profile enters only when somebody explicitly lists it. So a beta cohort of
// 38 profiles showed 3 cards, and no privacy setting was involved: the other
// 35 had simply never been listed into a table this screen should not have
// been reading.
//
//     asked     is this profile listed
//     mattered  does this profile exist here
//
// `GET /people/browse` is the pool, and it already carries the rule the
// product means: every active, non-anonymous profile, with the owner's
// private switch (`profiles.unlisted`, default 0) as the door out. Friends
// has read it all along. Discover reads it now too, and the marketplace
// supplies tags and blurbs for the profiles that have them — a listing makes
// a card richer, it no longer decides whether the card exists.
//
// The Marketplace screen keeps reading the marketplace. Opt-in is right for a
// storefront; it was only ever wrong here.
export function Discover({ onPlans, onVisit }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
  /** Open a profile's public page. A discovery card you cannot open is a
   *  storefront with no door — the field report tried every card. */
  onVisit: (profileId: string) => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  type Card = Awaited<ReturnType<typeof api.marketplace>>[number] & {
    verified?: boolean;
    /** What they do, off the pool row — the marketplace listing does not
     *  carry it, and the pool is where every card on this screen starts. */
    industry?: string | null;
    job_title?: string | null;
  };
  const [cards, setCards] = useState<Card[]>([]);
  // Who is already on the list. Every card said "Add friend", including
  // the ones added long ago — the button was an offer to people it had
  // already taken up on it. The label is the state: an added friend's
  // card says "Friends", and only a stranger's card offers.
  const [pals, setPals] = useState<Set<string>>(new Set());
  const [headCount, setHeadCount] = useState<number | null>(null);
  const [tag, setTag] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<unknown>(null);

  function load(t?: string) {
    // Two calls, deliberately. The pool answers *who is here*; the listing
    // answers *what they say about themselves*. Asking only the second is
    // the defect this screen shipped with.
    Promise.all([api.browsePeople(), api.marketplace(t || undefined)])
      .then(([pool, listings]) => {
        const extra = new Map(listings.map((l) => [l.profile_id, l]));
        const merged: Card[] = pool.found.map((p) => {
          const l = extra.get(p.profile_id);
          return {
            profile_id: p.profile_id,
            display_name: p.display_name,
            purpose: l?.purpose ?? null,
            tags: l?.tags ?? [],
            blurb: l?.blurb ?? null,
            avatar: p.avatar,
            // Server-decided on both sides, so a face is badged the same
            // whichever pool the card came from.
            avatar_kind: l?.avatar_kind ?? p.avatar_kind,
            industry: p.industry,
            job_title: p.job_title,
            verified: Boolean(
              (p.verification as { verified?: boolean } | null)?.verified),
          } as Card;
        });
        // A tag filter is a marketplace question — only listed profiles carry
        // tags — so filtering narrows to the listings that match rather than
        // silently emptying the pool.
        setCards(t ? merged.filter((c) => c.tags.length > 0) : merged);
        setHeadCount(pool.head_count);
      })
      .catch((e) => setError(e));
  }
  useEffect(() => load(), []);
  useEffect(() => {
    if (!session.profileId) return;
    api.friends(session.profileId)
      .then((r) => setPals(new Set(r.friends.map((f) => f.profile_id))))
      .catch(() => setPals(new Set()));
  }, [session.profileId]);

  async function installStarters() {
    setBusy(true); setError(null); setNote(null);
    try {
      const r = await api.seedStarters();
      setNote(tr("dsc.ready", lang)
        .replace("{made}", String(r.created.length))
        .replace("{had}", String(r.skipped.length)));
      load();
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  async function befriend(profileId: string) {
    if (!session.profileId || !session.ownerToken) {
      setError(tr("dsc.signin", lang)); return;
    }
    setBusy(true); setError(null);
    try {
      const said = await api.addFriend(
        session.profileId, profileId, session.ownerToken);
      // A 200 is not a yes — see `FriendAddition`. Somebody already on the
      // list answers `added: false`, and reporting that as "Added" is the
      // console telling a person something it was told was not true.
      setNote(said.added ? tr("dsc.added", lang)
                         : tr("dsc.already", lang));
      // Either verdict means the friendship stands now, and the card's
      // button should say so without a reload.
      setPals((was) => new Set(was).add(profileId));
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("dsc.title", lang)}</h2>
        <span className="muted small">{tr("dsc.pitch", lang)}</span>
        {/* The honest population, from the pool's own count rather than the
            length of this page. A screen showing three cards out of
            thirty-eight looked like a quiet deployment; it was a screen
            reading the wrong table, and a head count says which. */}
        {headCount !== null && (
          <span className="muted small">
            {tr("dsc.headcount", lang).replace("{n}", String(headCount))}
          </span>
        )}
      </header>

      {cards.length === 0 && (
        <div className="card">
          <h3>{tr("dsc.nothinglisted", lang)}</h3>
          <p className="muted small">{tr("dsc.starters", lang)}</p>
          <button className="primary" disabled={busy} onClick={installStarters}>
            {busy ? tr("dsc.installing", lang) : tr("dsc.install", lang)}
          </button>
        </div>
      )}

      {cards.length > 0 && (
        <div className="card">
          <div className="row">
            <label>{tr("dsc.filter", lang)}
              <input value={tag} placeholder={tr("dsc.tag.ph", lang)}
                     onChange={(e) => setTag(e.target.value)} />
            </label>
            <button onClick={() => load(tag.trim())}>
              {tr("dsc.search", lang)}
            </button>
            <button disabled={busy} onClick={installStarters}>
              {busy ? "…" : tr("dsc.refresh", lang)}
            </button>
          </div>
        </div>
      )}

      <div className="discover-grid">
        {cards.map((c) => (
          <div key={c.profile_id} className="card discover-card">
            <button className="dc-open" onClick={() => onVisit(c.profile_id)}
                    aria-label={c.display_name}>
            <div className="dc-face">
              {c.avatar ? (
                <img className="dc-avatar" src={getBase() + c.avatar}
                     alt={c.display_name} />
              ) : (
                <span className="dc-avatar dc-initials">
                  {c.display_name.split(/\s+/).map((w) => w[0]).join("").slice(0, 2)}
                </span>
              )}
              {/* The AI mark rides ON the picture, hung off its corner, in
                  the standard badge — the same one the talk face and the
                  room seat wear. It sat under the portrait for years
                  because a field report showed a pill swallowing the face
                  once a phone's font boosting inflated it; the pill is
                  pinned against boosting and grows outward from a corner
                  now, so that reason has been answered rather than
                  overruled. See `.dc-ai`.

                  The other two labels stay below. They are different
                  claims — the face is authentic, the person is who they
                  say — and three pills on one 64px circle is a face
                  nobody can see. */}
              {c.avatar_kind === "ai" && (
                <span className="ai-pill dc-ai">
                  {tr("dsc.badge.ai", lang)}
                </span>
              )}
            </div>
            {c.avatar_kind === "real_photo" && (
              <span className="dc-badge real">{tr("dsc.badge.real", lang)}</span>
            )}
            {c.verified && (
              <span className="dc-badge verified">
                {tr("dsc.badge.verified", lang)}
              </span>
            )}
            <b>{c.display_name}</b>
            </button>
            <Trade industry={c.industry} position={c.job_title}
                   className="card-trade" />
            {c.blurb && <p className="muted small">{c.blurb}</p>}
            <div className="tag-row">
              {c.tags.slice(0, 4).map((t) => <span key={t} className="tag">{t}</span>)}
            </div>
            {pals.has(c.profile_id) ? (
              <button className="primary is-friends" disabled>
                {tr("dsc.friends", lang)}
              </button>
            ) : (
              <button className="primary" disabled={busy}
                      onClick={() => befriend(c.profile_id)}>
                {tr("dsc.addfriend", lang)}
              </button>
            )}
          </div>
        ))}
      </div>

      {note && <div className="muted small">{note}</div>}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
