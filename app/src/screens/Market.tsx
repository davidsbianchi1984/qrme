import { useEffect, useState } from "react";
import { api, type Listing, type Locality, type MarketPrefs, type MarketSearch,
         type Offer, type Order } from "../api";
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
      setNote(`Bought — order ${order.id}, ${order.status}. ${order.payment}`);
      if (token) api.sales(token).then((r) => setSales(r.sales)).catch(() => undefined);
    } catch (e) { fail(e); }
  }

  const rows = found ? found.results : listings;

  return (
    <div className="screen">
      <h2>Marketplace</h2>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Find something</h3>
        <div className="row">
          <input value={q} onChange={(e) => setQ(e.target.value)}
                 placeholder="a plumber, a therapist, a tutor…"
                 onKeyDown={(e) => e.key === "Enter" && search()} />
          <button onClick={search}>Search</button>
          <button onClick={suggest}>Suggest words</button>
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
              {found.total} result{found.total === 1 ? "" : "s"} for
              “{found.query}”, scope {found.scope}
              {found.hidden_by_place > 0 &&
                <> · {found.hidden_by_place} hidden by where you are looking</>}
            </p>
            {/* The backend's own sentence, not ours. */}
            <p className="muted small"><em>{found.ranking}</em></p>
          </>
        )}
      </div>

      <div className="card">
        <h3>{found ? "Results" : "Everything listed"}</h3>
        {rows.length === 0 && <p className="muted small">Nothing here.</p>}
        {rows.map((l) => (
          <div key={l.id} className="row">
            <div style={{ flex: 1 }}>
              <strong>{l.title}</strong>
              <div className="muted small">{l.blurb}</div>
              <div className="muted small">
                {l.tags.join(" · ")}{l.provider_name && <> — {l.provider_name}</>}
              </div>
            </div>
            <button onClick={() => loadOffer(l.id)}>Price</button>
            {offers[l.id] && (
              <>
                <span>
                  {offers[l.id]!.price.toFixed(2)} {offers[l.id]!.currency}
                  {offers[l.id]!.stock !== null && <> · {offers[l.id]!.stock} left</>}
                </span>
                <button disabled={!token || offers[l.id]!.status !== "open"}
                        onClick={() => buy(offers[l.id]!)}>Buy</button>
              </>
            )}
          </div>
        ))}
        {Object.values(offers).some(Boolean) && (
          <p className="muted small">
            {Object.values(offers).find(Boolean)!.payment}
          </p>
        )}
      </div>

      <div className="card">
        <h3>Where you are looking</h3>
        {!token && <p className="muted small">Sign in to set this.</p>}
        {prefs && (
          <>
            <div className="row">
              <input value={prefs.locality || ""} placeholder="town"
                     onChange={(e) => setPrefs({ ...prefs, locality: e.target.value })} />
              <select value={prefs.scope}
                      onChange={(e) => setPrefs({ ...prefs, scope: e.target.value })}>
                <option value="anywhere">anywhere</option>
                <option value="locality">this town</option>
                <option value="region">this region</option>
              </select>
              <label>
                <input type="checkbox" checked={prefs.include_remote}
                       onChange={(e) =>
                         setPrefs({ ...prefs, include_remote: e.target.checked })} />
                {" "}remote counts
              </label>
              <button onClick={async () => {
                try {
                  setPrefs(await api.setMarketSettings(me, {
                    locality: prefs.locality, scope: prefs.scope,
                    include_remote: prefs.include_remote,
                  }, token));
                  setNote("Saved.");
                } catch (e) { fail(e); }
              }}>Save</button>
            </div>
            <p className="muted small">
              Yours alone, behind your own token. It narrows what you see and
              nothing else — it does not tell a seller where you are.
            </p>
          </>
        )}
      </div>

      <div className="card">
        <h3>Put this profile in the directory</h3>
        <p className="muted small">
          Different from a listing: a listing sells one thing, this puts the
          profile itself where people browsing can find it. Tags are how they
          find it, and the card shows display information only — never
          anything from inside the persona.
        </p>
        <div className="row">
          <input value={tags} onChange={(e) => setTags(e.target.value)}
                 placeholder="tags, comma separated" style={{ flex: 1 }} />
          <input value={blurb} onChange={(e) => setBlurb(e.target.value)}
                 placeholder="a line about it" style={{ flex: 1 }} />
          <button disabled={!session.profileId || !session.ownerToken}
                  onClick={async () => {
                    setError(null); setNote(null);
                    try {
                      await api.listOnMarketplace(session.profileId!, {
                        tags: tags.split(",").map((t) => t.trim())
                                  .filter(Boolean),
                        blurb: blurb.trim() || undefined },
                        session.ownerToken!);
                      setNote("Listed.");
                    } catch (e) { fail(e); }
                  }}>List it</button>
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
                      setNote("Taken out of the directory.");
                    } catch (e) { fail(e); }
                  }}>take it out</button>
        </div>
        <p className="muted small">
          Listing again replaces the tags and the line rather than adding a
          second row — one profile is in the directory once.
        </p>
      </div>

      <div className="card">
        <h3>Towns with listings</h3>
        {localities.length === 0 &&
          <p className="muted small">
            Nothing is placed yet. A listing with no place is everywhere, which
            is the same as nowhere when somebody is looking for help nearby.
          </p>}
        {localities.map((l) => (
          <div key={l.locality + (l.region || "")} className="row">
            <strong>{l.locality}</strong>
            {l.region && <span className="muted">{l.region}</span>}
            <span className="muted">{l.listings} listing{l.listings === 1 ? "" : "s"}</span>
          </div>
        ))}
      </div>

      {sales.length > 0 && (
        <div className="card">
          <h3>What you have sold</h3>
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
