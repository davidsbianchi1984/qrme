import { useEffect, useState } from "react";
import { api, type Listing, type Locality, type MarketPrefs, type MarketSearch,
         type Offer, type Order } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The marketplace: browsing, searching, placing, pricing, buying, and the
 * seller's own statement.
 *
 * All of it existed in the backend with no caller at all. Thirteen routes,
 * including the whole of the money path — you could not put a price on a
 * listing, and nobody could buy one.
 *
 * Two things this screen shows rather than paraphrases, because the backend
 * says them itself and a paraphrase could drift from what the code does:
 *
 * - the ranking sentence on a search ("deterministic — title, tags, provider,
 *   blurb, in that order. No model reorders this."), because a marketplace
 *   that quietly ranked by anything else would be a different product;
 * - the payment note on an offer, which states plainly that the money is
 *   simulated. Money that looks real and is not is the one thing here it
 *   would be worst to be vague about.
 */
export function Market({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.interactorId || "";
  const token = session.interactorToken || "";

  const [listings, setListings] = useState<Listing[]>([]);
  const [localities, setLocalities] = useState<Locality[]>([]);
  const [q, setQ] = useState("");
  const [found, setFound] = useState<MarketSearch | null>(null);
  const [ideas, setIdeas] = useState<string[]>([]);
  const [prefs, setPrefs] = useState<MarketPrefs | null>(null);
  const [offers, setOffers] = useState<Record<string, Offer | null>>({});
  const [sales, setSales] = useState<Order[]>([]);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [tags, setTags] = useState("");
  const [blurb, setBlurb] = useState("");
  // Which folder of the shelved catalogue is open. One at a time — the
  // point of folders is not seeing everything at once.
  const [openFolder, setOpenFolder] = useState<string | null>(null);

  const fail = (e: unknown) => setError(e);

  useEffect(() => {
    api.marketplaceListings().then(setListings).catch(fail);
    api.marketLocalities().then(setLocalities).catch(fail);
  }, []);

  useEffect(() => {
    if (!me || !token) return;
    api.marketSettings(me, token).then(setPrefs).catch(() => undefined);
    api.sales(token).then((r) => setSales(r.sales)).catch(() => undefined);
  }, [me, token]);

  async function search() {
    setError(null);
    try {
      setFound(await api.marketSearch(q, me || undefined));
    } catch (e) { fail(e); }
  }

  // Suggestions for the box, and nothing else — the reply says `applied:
  // false` and the caption below repeats it, because a suggestion that had
  // quietly filtered the results would be a different promise.
  async function suggest() {
    if (!q.trim()) return;
    try {
      const a = await api.marketAssist(q);
      setIdeas(a.suggestions);
      setNote(a.note);
    } catch (e) { fail(e); }
  }

  async function loadOffer(id: string) {
    try {
      setOffers((o) => ({ ...o, [id]: null }));
      const found = await api.offer(id);
      setOffers((o) => ({ ...o, [id]: found }));
    } catch {
      // 404 here means "not for sale", which is an ordinary state for a
      // listing rather than a failure worth a banner.
      setOffers((o) => ({ ...o, [id]: null }));
    }
  }

  async function buy(o: Offer) {
    setError(null); setNote(null);
    try {
      const order = await api.purchase(o.listing_id, o.price, token);
      setNote(tr("mkt.bought.said", lang)
        .replace("{id}", order.id)
        .replace("{status}", order.status)
        .replace("{payment}", order.payment));
      if (token) api.sales(token).then((r) => setSales(r.sales)).catch(() => undefined);
    } catch (e) { fail(e); }
  }

  const rows = found ? found.results : listings;

  // The shelves: a listing's first tag is its folder. Search results stay
  // flat — a search is already a filter — but browsing gets folders, so a
  // long catalogue is a shelf to open rather than a wall to scroll.
  const folders = new Map<string, Listing[]>();
  if (!found) {
    for (const l of listings) {
      const f = (l.tags[0] || "").trim().toLowerCase();
      folders.set(f, [...(folders.get(f) || []), l]);
    }
  }
  const folderNames = [...folders.keys()]
    .sort((a, b) => (folders.get(b)!.length - folders.get(a)!.length) ||
                    a.localeCompare(b));

  const listingRow = (l: Listing) => (
    <div key={l.id} className="row">
      <div style={{ flex: 1 }}>
        <strong>{l.title}</strong>
        <div className="muted small">{l.blurb}</div>
        <div className="muted small">
          {l.tags.join(" · ")}{l.provider_name && <> — {l.provider_name}</>}
        </div>
      </div>
      <button onClick={() => loadOffer(l.id)}>
        {tr("mkt.price", lang)}
      </button>
      {offers[l.id] && (
        <>
          <span>
            {offers[l.id]!.price.toFixed(2)} {offers[l.id]!.currency}
            {offers[l.id]!.stock !== null && fill(tr("mkt.left", lang),
              { n: offers[l.id]!.stock })}
          </span>
          <button disabled={!token || offers[l.id]!.status !== "open"}
                  onClick={() => buy(offers[l.id]!)}>
            {tr("mkt.buy", lang)}
          </button>
        </>
      )}
    </div>
  );

  return (
    <div className="screen">
      <h2>{tr("mkt.title", lang)}</h2>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("mkt.find", lang)}</h3>
        <div className="row">
          <input value={q} onChange={(e) => setQ(e.target.value)}
                 placeholder={tr("mkt.q.ph", lang)}
                 onKeyDown={(e) => e.key === "Enter" && search()} />
          <button onClick={search}>{tr("mkt.search", lang)}</button>
          <button onClick={suggest}>{tr("mkt.suggest", lang)}</button>
        </div>
        {ideas.length > 0 && (
          <div className="row">
            {ideas.map((s) => (
              <button key={s} className="chip"
                      onClick={() => { setQ(s); setIdeas([]); }}>{s}</button>
            ))}
          </div>
        )}
        {found && (
          <>
            <p className="muted small">
              {fill(found.total === 1
                ? tr("mkt.result", lang) : tr("mkt.results", lang), {
                n: found.total, q: found.query, scope: found.scope })}
              {found.hidden_by_place > 0 && fill(tr("mkt.hidden", lang),
                { n: found.hidden_by_place })}
            </p>
            {/* The backend's own sentence, not ours. */}
            <p className="muted small"><em>{found.ranking}</em></p>
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("mkt.where", lang)}</h3>
        {!token &&
          <p className="muted small">{tr("mkt.signin", lang)}</p>}
        {prefs && (
          <>
            <div className="row">
              <input value={prefs.locality || ""} placeholder={tr("mkt.town.ph", lang)}
                     onChange={(e) => setPrefs({ ...prefs, locality: e.target.value })} />
              <select value={prefs.scope}
                      onChange={(e) => setPrefs({ ...prefs, scope: e.target.value })}>
                <option value="anywhere">{tr("mkt.anywhere", lang)}</option>
                <option value="locality">{tr("mkt.thistown", lang)}</option>
                <option value="region">{tr("mkt.thisregion", lang)}</option>
              </select>
              <label>
                <input type="checkbox" checked={prefs.include_remote}
                       onChange={(e) =>
                         setPrefs({ ...prefs, include_remote: e.target.checked })} />
                {" "}{tr("mkt.remote", lang)}
              </label>
              <button onClick={async () => {
                try {
                  setPrefs(await api.setMarketSettings(me, {
                    locality: prefs.locality, scope: prefs.scope,
                    include_remote: prefs.include_remote,
                  }, token));
                  setNote(tr("mkt.saved.said", lang));
                } catch (e) { fail(e); }
              }}>{tr("mkt.save", lang)}</button>
            </div>
            <p className="muted small">{tr("mkt.yoursalone", lang)}</p>
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("mkt.directory", lang)}</h3>
        <p className="muted small">{tr("mkt.directory.pitch", lang)}</p>
        <div className="row">
          <input value={tags} onChange={(e) => setTags(e.target.value)}
                 placeholder={tr("mkt.tags.ph", lang)} style={{ flex: 1 }} />
          <input value={blurb} onChange={(e) => setBlurb(e.target.value)}
                 placeholder={tr("mkt.blurb.ph", lang)} style={{ flex: 1 }} />
          <button disabled={!session.profileId || !session.ownerToken}
                  onClick={async () => {
                    setError(null); setNote(null);
                    try {
                      await api.listOnMarketplace(session.profileId!, {
                        tags: tags.split(",").map((t) => t.trim())
                                  .filter(Boolean),
                        blurb: blurb.trim() || undefined },
                        session.ownerToken!);
                      setNote(tr("mkt.listed.said", lang));
                    } catch (e) { fail(e); }
                  }}>{tr("mkt.listit", lang)}</button>
          {/* Unlisting a profile that is not listed is a 404, so the
              refusal carries the fact rather than the button pretending it
              worked. The friends delete next door answers 200 for the same
              situation, which is why that one reads a flag instead. */}
          <button className="chip"
                  disabled={!session.profileId || !session.ownerToken}
                  onClick={async () => {
                    setError(null); setNote(null);
                    try {
                      await api.unlistFromMarketplace(session.profileId!,
                                                      session.ownerToken!);
                      setNote(tr("mkt.tookout.said", lang));
                    } catch (e) { fail(e); }
                  }}>{tr("mkt.takeout", lang)}</button>
        </div>
        <p className="muted small">{tr("mkt.replaces", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("mkt.towns", lang)}</h3>
        {localities.length === 0 &&
          <p className="muted small">{tr("mkt.noplace", lang)}</p>}
        {localities.map((l) => (
          <div key={l.locality + (l.region || "")} className="row">
            <strong>{l.locality}</strong>
            {l.region && <span className="muted">{l.region}</span>}
            <span className="muted">
              {fill(l.listings === 1
                ? tr("mkt.listing", lang) : tr("mkt.listings", lang),
                { n: l.listings })}
            </span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>
          {found ? tr("mkt.hdr.results", lang) : tr("mkt.hdr.all", lang)}
        </h3>
        {rows.length === 0 &&
          <p className="muted small">{tr("mkt.nothinghere", lang)}</p>}
        {/* Search results stay flat; browsing gets folders — a listing's
            first tag is its shelf, opened one at a time. */}
        {found && rows.map(listingRow)}
        {!found && folderNames.length > 0 && (
          <>
            <p className="muted small">{tr("mkt.folders.pitch", lang)}</p>
            <div className="actions" style={{ marginTop: 0 }}>
              {folderNames.map((f) => (
                <button key={f || "other"} className="chip"
                        onClick={() =>
                          setOpenFolder(openFolder === f ? null : f)}>
                  {(f || tr("mkt.folder.other", lang))
                    + " · " + folders.get(f)!.length}
                </button>
              ))}
            </div>
            {openFolder !== null && folders.has(openFolder) &&
              folders.get(openFolder)!.map(listingRow)}
          </>
        )}
        {Object.values(offers).some(Boolean) && (
          <p className="muted small">
            {Object.values(offers).find(Boolean)!.payment}
          </p>
        )}
      </div>

      {sales.length > 0 && (
        <div className="card">
          <h3>{tr("mkt.sold", lang)}</h3>
          {sales.map((s) => (
            <div key={s.id} className="row">
              <strong>{s.title}</strong>
              <span>{s.price.toFixed(2)} {s.currency}</span>
              <span className="muted">{s.status}</span>
              <span className="muted small">{s.created_at.slice(0, 10)}</span>
            </div>
          ))}
          <p className="muted small">{sales[0].payment}</p>
        </div>
      )}
    </div>
  );
}
