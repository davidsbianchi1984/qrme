import { useCallback, useEffect, useState } from "react";
import {
  api, type ShopCard, type ShopDetail, type ShopOrder,
} from "../api";
import { Refusal } from "../Refusal";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

// A storefront, not a counter.
//
// The desk promises a *person*, present now, who can open connections. A
// shop promises none of that: it lists what a business or a person sells —
// goods and services with prices and availability — takes an order, and
// settles it. The two share nothing but the marketplace they both stand in,
// and this screen deliberately has no session, no bell and no offer UI.
//
// Two hats, one screen: browsing (any visitor, with an interactor token to
// buy) and the till (the profile owner who sells). The seller's half signs
// with the owner token already in the session; the buyer's half asks for
// the interactor token because buying is the interactor's own act — the
// same identity a conversation runs on, and the one JIM's tandem holds.
export function Shops({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [cards, setCards] = useState<ShopCard[]>([]);
  const [tag, setTag] = useState("");
  const [open, setOpen] = useState<ShopDetail | null>(null);

  // The buyer's hat.
  const [buyerId, setBuyerId] = useState("");
  const [buyerToken, setBuyerToken] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [mine, setMine] = useState<ShopOrder[]>([]);

  // The seller's hat.
  const [shopName, setShopName] = useState("");
  const [shopBlurb, setShopBlurb] = useState("");
  const [shopTag, setShopTag] = useState("");
  const [myShop, setMyShop] = useState<ShopDetail | null>(null);
  const [book, setBook] = useState<ShopOrder[]>([]);
  const [offer, setOffer] = useState({ kind: "goods", title: "", price: "" });

  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  const load = useCallback((t?: string) => {
    api.listShops(t || undefined).then(setCards).catch((e) => setError(e));
  }, []);
  useEffect(() => load(), [load]);

  async function run(op: () => Promise<void>) {
    setBusy(true); setError(null); setNote(null);
    try { await op(); } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  function browse(shopId: string) {
    run(async () => setOpen(await api.shopCard(shopId)));
  }

  function order(offeringId: string) {
    if (!open) return;
    run(async () => {
      const placed = await api.placeShopOrder(open.id, {
        offering_id: offeringId, buyer_id: buyerId,
        quantity: Number(quantity) || 1,
      }, buyerToken);
      setNote(`${tr("shops.ordered", lang)} · ${placed.status}`);
      setMine(await api.myShopOrders(buyerId, buyerToken));
    });
  }

  function cancel(o: ShopOrder) {
    run(async () => {
      await api.advanceShopOrder(o.shop_id, o.id,
        { party: "buyer", to: "cancelled" }, buyerToken);
      setMine(await api.myShopOrders(buyerId, buyerToken));
    });
  }

  function openTill() {
    if (!session.profileId || !session.ownerToken) {
      setError(tr("shops.signin", lang)); return;
    }
    run(async () => {
      const shop = await api.openShop({
        profile_id: session.profileId!, name: shopName,
        blurb: shopBlurb || undefined, tag: shopTag || undefined,
      }, session.ownerToken!);
      setMyShop(shop);
      setBook(await api.shopOrderBook(shop.id, session.ownerToken!));
      load();
    });
  }

  function addOffering() {
    if (!myShop || !session.ownerToken) return;
    run(async () => {
      await api.addOffering(myShop.id, {
        kind: offer.kind, title: offer.title, price: Number(offer.price) || 0,
      }, session.ownerToken!);
      setOffer({ kind: "goods", title: "", price: "" });
      setMyShop(await api.shopCard(myShop.id));
      load();
    });
  }

  function retire(offeringId: string) {
    if (!myShop || !session.ownerToken) return;
    run(async () => {
      await api.retireOffering(myShop.id, offeringId, session.ownerToken!);
      setMyShop(await api.shopCard(myShop.id));
    });
  }

  function advance(o: ShopOrder, to: string) {
    if (!myShop || !session.ownerToken) return;
    run(async () => {
      await api.advanceShopOrder(o.shop_id, o.id, { party: "seller", to },
                                 session.ownerToken!);
      setBook(await api.shopOrderBook(myShop.id, session.ownerToken!));
    });
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("shops.title", lang)}</h2>
        <span className="muted small">{tr("shops.sub", lang)}</span>
      </header>

      <div className="card">
        <div className="row">
          <label>{tr("shops.filter", lang)}
            <input value={tag} onChange={(e) => setTag(e.target.value)} />
          </label>
          <button onClick={() => load(tag.trim())}>{tr("shops.search", lang)}</button>
        </div>
        {cards.length === 0 && (
          <p className="muted small">{tr("shops.none", lang)}</p>
        )}
        {cards.map((s) => (
          <div key={s.id} className="row" style={{ justifyContent: "space-between" }}>
            <span>{s.name} · <span className="muted small">{s.seller}
              {s.tag ? ` · ${s.tag}` : ""} · {s.offerings}</span></span>
            <button onClick={() => browse(s.id)}>{tr("shops.browse", lang)}</button>
          </div>
        ))}
      </div>

      {open && (
        <div className="card">
          <h3>{open.name}</h3>
          {open.blurb && <p className="muted small">{open.blurb}</p>}
          <div className="row">
            <label>{tr("shops.buyer_id", lang)}
              <input value={buyerId} onChange={(e) => setBuyerId(e.target.value)} />
            </label>
            <label>{tr("shops.buyer_token", lang)}
              <input type="password" value={buyerToken}
                     onChange={(e) => setBuyerToken(e.target.value)} />
            </label>
            <label>{tr("shops.quantity", lang)}
              <input value={quantity} onChange={(e) => setQuantity(e.target.value)} />
            </label>
          </div>
          {open.offerings.map((o) => (
            <div key={o.id} className="row" style={{ justifyContent: "space-between" }}>
              <span>{o.title} · <span className="muted small">
                {o.kind} · {o.price} {o.currency} · {o.availability}</span></span>
              <button disabled={busy || !buyerId || !buyerToken}
                      onClick={() => order(o.id)}>{tr("shops.order", lang)}</button>
            </div>
          ))}
          {mine.length > 0 && <h3>{tr("shops.mine", lang)}</h3>}
          {mine.map((o) => (
            <div key={o.id} className="row" style={{ justifyContent: "space-between" }}>
              <span>{o.title} · {o.amount} {o.currency} ·{" "}
                <span className="muted small">{o.status}</span></span>
              {o.status === "placed" && (
                <button disabled={busy} onClick={() => cancel(o)}>
                  {tr("shops.cancel", lang)}</button>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h3>{tr("shops.till", lang)}</h3>
        <p className="muted small">{tr("shops.till_note", lang)}</p>
        <div className="row">
          <label>{tr("shops.name", lang)}
            <input value={shopName} onChange={(e) => setShopName(e.target.value)} />
          </label>
          <label>{tr("shops.tag", lang)}
            <input value={shopTag} onChange={(e) => setShopTag(e.target.value)} />
          </label>
        </div>
        <label>{tr("shops.blurb", lang)}
          <input value={shopBlurb} onChange={(e) => setShopBlurb(e.target.value)} />
        </label>
        <button className="primary" disabled={busy || !shopName.trim()}
                onClick={openTill}>{tr("shops.open", lang)}</button>

        {myShop && (
          <>
            <div className="row">
              <label>{tr("shops.offer_title", lang)}
                <input value={offer.title}
                       onChange={(e) => setOffer({ ...offer, title: e.target.value })} />
              </label>
              <label>{tr("shops.price", lang)}
                <input value={offer.price}
                       onChange={(e) => setOffer({ ...offer, price: e.target.value })} />
              </label>
              <label>{tr("shops.kind", lang)}
                <select value={offer.kind}
                        onChange={(e) => setOffer({ ...offer, kind: e.target.value })}>
                  <option value="goods">{tr("shops.goods", lang)}</option>
                  <option value="service">{tr("shops.service", lang)}</option>
                </select>
              </label>
              <button disabled={busy || !offer.title.trim()}
                      onClick={addOffering}>{tr("shops.add", lang)}</button>
            </div>
            {myShop.offerings.map((o) => (
              <div key={o.id} className="row" style={{ justifyContent: "space-between" }}>
                <span>{o.title} · {o.price} {o.currency}</span>
                <button disabled={busy} onClick={() => retire(o.id)}>
                  {tr("shops.retire", lang)}</button>
              </div>
            ))}
            {book.length > 0 && <h3>{tr("shops.book", lang)}</h3>}
            {book.map((o) => (
              <div key={o.id} className="row" style={{ justifyContent: "space-between" }}>
                <span>{o.title} ×{o.quantity} · {o.amount} {o.currency} ·{" "}
                  <span className="muted small">{o.status}</span></span>
                <span>
                  {o.status === "placed" && (
                    <>
                      <button disabled={busy} onClick={() => advance(o, "accepted")}>
                        {tr("shops.accept", lang)}</button>
                      <button disabled={busy} onClick={() => advance(o, "declined")}>
                        {tr("shops.decline", lang)}</button>
                    </>
                  )}
                  {o.status === "accepted" && (
                    <button disabled={busy} onClick={() => advance(o, "fulfilled")}>
                      {tr("shops.fulfil", lang)}</button>
                  )}
                </span>
              </div>
            ))}
          </>
        )}
      </div>

      {note && <div className="muted small">{note}</div>}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
