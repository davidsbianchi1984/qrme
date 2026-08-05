import { useEffect, useState } from "react";
import { api, type EarningsStatement, type LicenseHolder,
         type LicenseOfferView, type Offer, type PayoutReceipt } from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The other side of the counter.
 *
 * `Leaving` is the buyer's screen: acquire a licence, derive an agent. This
 * is the seller's, and until this round the console did not have one. An
 * owner could be *bought from* and could not post the offer, see who held a
 * licence, revoke one, read a penny of what it earned, or ask to be paid.
 * Nine routes, all owner-side.
 *
 * They were not on the doorless backlog because the audit unioned the console
 * with the iOS, Android and Windows shells, and all three of those have an
 * Earn tab. So the guard answered *some client can reach this*, which was
 * true, in place of *this client can reach this*, which was not — a desktop
 * owner had to install the phone app to get paid.
 *
 * ## Two figures that were one
 *
 * The statement used to sum every entry regardless of currency and label the
 * result with whichever sale was newest: ¥100 and $100 came back as
 * `accrued: 200`. Totals are now per currency, `totals` states the settlement
 * currency's, and `mixed` says whether there is a balance the headline leaves
 * out. This screen reads `mixed` before it draws a figure — a number with a
 * currency symbol in front of it is a claim, and it has to be one that holds.
 *
 * A payout settles one currency. `remaining` is why the button can say
 * *paid, and there is more* rather than just *paid*.
 *
 * ## Revoking is not undoing
 *
 * Revoking a licence stops the buyer deriving from it. It does not unmake an
 * agent they already derived, and it does not remove the fee from the
 * statement. The screen says all three, because a control labelled "revoke"
 * that quietly did fewer things than the word suggests is worse than no
 * control.
 */
export function Selling({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [offer, setOffer] = useState<LicenseOfferView | null>(null);
  const [holders, setHolders] = useState<LicenseHolder[]>([]);
  const [statement, setStatement] = useState<EarningsStatement | null>(null);
  const [receipt, setReceipt] = useState<PayoutReceipt | null>(null);

  const [kind, setKind] = useState("consult");
  const [price, setPrice] = useState("250");
  const [currency, setCurrency] = useState("USD");
  const [terms, setTerms] = useState("");

  const [listingTitle, setListingTitle] = useState("");
  const [listingBlurb, setListingBlurb] = useState("");
  const [listingId, setListingId] = useState("");
  const [askPrice, setAskPrice] = useState("");
  const [stock, setStock] = useState("");
  const [locality, setLocality] = useState("");
  const [region, setRegion] = useState("");
  const [remote, setRemote] = useState(false);
  const [offerOn, setOfferOn] = useState<Offer | null>(null);

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function load() {
    if (!me) return;
    // A 404 here means *not offered for licence*, which is the ordinary
    // state of most profiles and not a failure to report.
    api.licenseOffer(me).then(setOffer).catch(() => setOffer(null));
    if (!token) return;
    api.licenseHolders(me, token).then(setHolders).catch(() => setHolders([]));
    api.earnings(me, token).then(setStatement).catch(() => setStatement(null));
  }
  useEffect(load, [me, token]);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { setError(e); } finally { setBusy(false); }
  };

  const money = (n: number, ccy: string) =>
    `${n.toLocaleString(undefined, { minimumFractionDigits: 2 })} ${ccy}`;

  return (
    <div className="screen">
      <h2>{tr("sell.title", lang)}</h2>
      <p className="muted small">{tr("sell.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("sell.offer", lang)}</h3>
        {offer ? (
          <p className="small">
            <strong>{offer.kind}</strong> · {money(offer.price, offer.currency)}
            {offer.terms && ` · ${offer.terms}`}
            {offer.allow_derivatives
              ? " · a buyer may derive an agent"
              : " · consult only"}
          </p>
        ) : (
          <p className="muted small">{tr("sell.offer.none", lang)}</p>
        )}
        <p className="muted small">{tr("sell.offer.adult", lang)}</p>
        <div className="row">
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            <option value="consult">{tr("sell.kind.consult", lang)}</option>
            <option value="finetune">{tr("sell.kind.finetune", lang)}</option>
            <option value="clone">{tr("sell.kind.clone", lang)}</option>
          </select>
          <input value={price} onChange={(e) => setPrice(e.target.value)}
                 placeholder={tr("sell.offer.price.ph", lang)} style={{ width: "6rem" }} />
          <input value={currency} maxLength={3}
                 onChange={(e) => setCurrency(e.target.value.toUpperCase())}
                 placeholder={tr("sell.offer.ccy.ph", lang)} style={{ width: "5rem" }} />
          <input value={terms} onChange={(e) => setTerms(e.target.value)}
                 placeholder={tr("sell.offer.terms.ph", lang)} style={{ flex: 1 }} />
        </div>
        <div className="row">
          <button disabled={busy || !me || !token || !price.trim()}
                  onClick={act(async () => setOffer(
                    await api.setLicenseOffer(me, {
                      kind, price: Number(price), currency,
                      terms: terms.trim() || undefined,
                    }, token)), "Offered.")}>
            {tr("sell.offer.post", lang)}
          </button>
          {offer && (
            <button disabled={busy || !token}
                    onClick={act(async () => {
                      await api.withdrawLicenseOffer(me, token);
                      setOffer(null);
                    }, "Withdrawn. Licences already sold still stand.")}>
              {tr("sell.offer.stop", lang)}
            </button>
          )}
        </div>
      </div>

      <div className="card">
        <h3>{tr("sell.holders", lang)}</h3>
        {holders.length === 0 && (
          <p className="muted small">{tr("sell.holders.none", lang)}</p>
        )}
        {holders.map((h) => (
          <p className="small" key={h.id}>
            <code>{h.id}</code> · {h.kind} · {h.created_at}
            {h.derived_profile_id
              ? " · an agent has been derived from it"
              : " · nothing derived yet"}
            {h.revoked ? " · revoked" : ""}
            {!h.revoked && (
              <>
                {" "}
                <button disabled={busy || !token}
                        onClick={act(async () => {
                          await api.revokeLicense(h.id, token);
                        }, "Revoked.")}>
                  {tr("sell.holders.revoke", lang)}
                </button>
              </>
            )}
          </p>
        ))}
        <p className="muted small">{tr("sell.holders.rule", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("sell.earn", lang)}</h3>
        {!statement && (
          <p className="muted small">{tr("sell.earn.signin", lang)}</p>
        )}
        {statement && (
          <>
            <p className="small">
              {fill(tr("sell.earn.line", lang), {
                a: money(statement.totals.accrued, statement.currency),
                p: money(statement.totals.paid, statement.currency),
                l: money(statement.totals.lifetime, statement.currency),
              })}
            </p>
            {statement.totals.mixed && (
              <>
                {/* The headline covers one currency. Saying so is the whole
                    fix: these figures used to be added together. */}
                <p className="muted small">
                  {fill(tr("sell.earn.mixed", lang), {
                    ccy: statement.currency,
                    others: statement.currencies
                      .filter((c) => c !== statement.currency).join(", "),
                  })}
                </p>
                {statement.currencies.map((c) => (
                  <p className="small" key={c}>
                    {fill(tr("sell.earn.bycur", lang), {
                      c: <strong>{c}</strong>,
                      a: money(statement.by_currency[c].accrued, c),
                      p: money(statement.by_currency[c].paid, c),
                    })}
                  </p>
                ))}
              </>
            )}
            {statement.entries.length === 0 && (
              <p className="muted small">{tr("sell.earn.none", lang)}</p>
            )}
            {statement.entries.slice(0, 12).map((e) => (
              <p className="small" key={e.id}>
                {money(e.amount, e.currency)} · {e.kind} · {e.status}
                {e.memo && ` · ${e.memo}`}
              </p>
            ))}
            <button disabled={busy || !token
                              || statement.totals.accrued <= 0}
                    onClick={act(async () => setReceipt(
                      await api.requestPayout(me, token)))}>
              {tr("sell.earn.payout", lang)}
            </button>
            {statement.totals.mixed && statement.currencies
              .filter((c) => c !== statement.currency
                             && statement.by_currency[c].accrued > 0)
              .map((c) => (
                <button key={c} disabled={busy || !token}
                        onClick={act(async () => setReceipt(
                          await api.requestPayout(me, token, c)))}>
                  {fill(tr("sell.earn.payoutc", lang), { c })}
                </button>
              ))}
            {receipt && (
              <p className="muted small">
                {fill(tr("sell.earn.receipt", lang), {
                  total: money(receipt.total, receipt.currency),
                  n: receipt.entries,
                  note: receipt.note,
                })}
                {receipt.remaining.length > 0
                  && ` You still hold a balance in `
                     + `${receipt.remaining.join(", ")}.`}
              </p>
            )}
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("sell.listing", lang)}</h3>
        <p className="muted small">{tr("sell.listing.lead", lang)}</p>
        <div className="row">
          <input value={listingTitle}
                 onChange={(e) => setListingTitle(e.target.value)}
                 placeholder={tr("sell.listing.title.ph", lang)} style={{ flex: 1 }} />
          <input value={listingBlurb}
                 onChange={(e) => setListingBlurb(e.target.value)}
                 placeholder={tr("sell.listing.blurb.ph", lang)} style={{ flex: 1 }} />
        </div>
        <div className="row">
          <button disabled={busy || !token || !listingTitle.trim()}
                  onClick={act(async () => {
                    const made = await api.createListing({
                      kind: "profile", title: listingTitle.trim(),
                      blurb: listingBlurb.trim() || undefined,
                      provider_name: listingTitle.trim(),
                      profile_id: me,
                    }, token);
                    setListingId(made.id);
                  }, "Listed.")}>
            {tr("sell.listing.put", lang)}
          </button>
          <input value={listingId}
                 onChange={(e) => setListingId(e.target.value)}
                 placeholder={tr("sell.listing.id.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !token || !listingId.trim()}
                  onClick={act(async () => {
                    await api.removeListing(listingId.trim(), token);
                    setListingId("");
                  }, "Taken down.")}>
            {tr("sell.listing.down", lang)}
          </button>
        </div>
        <p className="muted small">{tr("sell.listing.rule", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("sell.price", lang)}</h3>
        <p className="muted small">{tr("sell.price.lead", lang)}</p>
        <div className="row">
          <input value={askPrice} onChange={(e) => setAskPrice(e.target.value)}
                 placeholder={tr("sell.offer.price.ph", lang)} style={{ width: "7rem" }} />
          <input value={stock} onChange={(e) => setStock(e.target.value)}
                 placeholder={tr("sell.price.stock.ph", lang)} style={{ flex: 1 }} />
        </div>
        <div className="row">
          <button disabled={busy || !token || !listingId.trim()
                            || !askPrice.trim()}
                  onClick={act(async () => setOfferOn(
                    await api.setOffer(listingId.trim(), {
                      price: Number(askPrice), currency,
                      stock: stock.trim() ? Number(stock) : undefined,
                    }, token)), "Priced.")}>
            {tr("sell.price.put", lang)}
          </button>
          <button disabled={busy || !token || !listingId.trim()}
                  onClick={act(async () => {
                    await api.withdrawOffer(listingId.trim(), token);
                    setOfferOn(null);
                  }, "Stopped selling it. The window stays; receipts stay.")}>
            {tr("sell.price.stop", lang)}
          </button>
        </div>
        {offerOn && (
          <p className="small">
            {money(offerOn.price, offerOn.currency)} · {offerOn.status} ·{" "}
            {fill(tr("sell.price.sold", lang), { n: offerOn.sold })}
            {offerOn.stock !== null && ` · ${offerOn.stock} left`}
          </p>
        )}
      </div>

      <div className="card">
        <h3>{tr("sell.place", lang)}</h3>
        <p className="muted small">{tr("sell.place.lead", lang)}</p>
        <div className="row">
          <input value={locality} onChange={(e) => setLocality(e.target.value)}
                 placeholder={tr("sell.place.loc.ph", lang)} style={{ flex: 1 }} />
          <input value={region} onChange={(e) => setRegion(e.target.value)}
                 placeholder={tr("sell.place.region.ph", lang)} style={{ width: "9rem" }} />
          <label className="small">
            <input type="checkbox" checked={remote}
                   onChange={(e) => setRemote(e.target.checked)} />
            {" "}{tr("sell.place.remote", lang)}
          </label>
        </div>
        <div className="row">
          <button disabled={busy || !token || !listingId.trim()
                            || !locality.trim()}
                  onClick={act(async () => {
                    await api.placeListing(listingId.trim(), {
                      locality: locality.trim(),
                      region: region.trim() || undefined, remote,
                    }, token);
                  }, "Placed.")}>
            {tr("sell.place.say", lang)}
          </button>
          <button disabled={busy || !token || !listingId.trim()}
                  onClick={act(async () => {
                    await api.unplaceListing(listingId.trim(), token);
                  }, "Cleared — it is offered anywhere again.")}>
            {tr("sell.place.clear", lang)}
          </button>
        </div>
      </div>
    </div>
  );
}
