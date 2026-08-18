import { useEffect, useState } from "react";
import { api, getBase } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// For You + the marketplace + the starter collection, one discovery surface.
// Everything here was already in the backend; the console just never showed
// the doors. The starter collection installs on demand (idempotent server
// side), and every card is a real profile you can befriend.
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
  const [cards, setCards] = useState<Awaited<ReturnType<typeof api.marketplace>>>([]);
  const [tag, setTag] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<unknown>(null);

  function load(t?: string) {
    api.marketplace(t || undefined).then(setCards).catch((e) => setError(e));
  }
  useEffect(() => load(), []);

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
      await api.addFriend(session.profileId, profileId, session.ownerToken);
      setNote(tr("dsc.added", lang));
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("dsc.title", lang)}</h2>
        <span className="muted small">{tr("dsc.pitch", lang)}</span>
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
            </div>
            {/* The kind label sits under the portrait, never on it — a
                field report showed the green pill swallowing the face
                once a phone's font boosting inflated it. */}
            {c.avatar_kind === "ai" && (
              <span className="dc-badge ai">{tr("dsc.badge.ai", lang)}</span>
            )}
            {c.avatar_kind === "real_photo" && (
              <span className="dc-badge real">{tr("dsc.badge.real", lang)}</span>
            )}
            <b>{c.display_name}</b>
            </button>
            {c.blurb && <p className="muted small">{c.blurb}</p>}
            <div className="tag-row">
              {c.tags.slice(0, 4).map((t) => <span key={t} className="tag">{t}</span>)}
            </div>
            <button className="primary" disabled={busy}
                    onClick={() => befriend(c.profile_id)}>
              {tr("dsc.addfriend", lang)}
            </button>
          </div>
        ))}
      </div>

      {note && <div className="muted small">{note}</div>}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
