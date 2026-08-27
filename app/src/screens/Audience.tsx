import { useEffect, useState } from "react";
import { api, type AudienceView, type GiftsView, type Order,
         type Subscription } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Who follows a profile, and what they pay.
 *
 * Two tiers, and no middle: `follow` is free and `paid` is not. The paid one
 * asks for two things a careless client would skip — an `accept_price` that
 * matches the price exactly, and a beneficiary — and both refusals name what
 * is missing rather than failing generically.
 *
 * **Nothing renews on a timer.** A period is charged when somebody presses
 * renew, which is why this screen has a button for it and no schedule: a
 * deployment left running does not accrue charges nobody authorised and
 * nobody saw. `periods` is therefore a count of deliberate acts, and the
 * screen says so rather than showing it as a duration.
 *
 * One asymmetry worth knowing, because the two routes look alike and are not:
 *
 * - a **gift** reads its beneficiary from the subject, so a giver cannot
 *   point money meant for a performer at their own balance;
 * - a **subscription** takes a beneficiary from the request body.
 *
 * The console sends the profile's own account for the second, and says which
 * account the money is credited to, because that is the part somebody paying
 * is entitled to see.
 *
 * Gifting refuses without a verified birthdate — *an unverified age is not
 * evidence of an adult* — and the cap is published so the limit can be shown
 * before somebody hits it rather than after.
 */
export function Audience({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";
  const account = session.accountId || "";
  const interactorToken = session.interactorToken || token;

  const [subject, setSubject] = useState("");
  const [mine, setMine] = useState<Subscription[]>([]);
  const [theirs, setTheirs] = useState<Subscription[]>([]);
  const [gifts, setGifts] = useState<GiftsView | null>(null);
  const [view, setView] = useState<AudienceView | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  // Who opened their door to this profile — an audience that asked,
  // rather than one the profile reached for (qrme/opendoor.py).
  const [openers, setOpeners] = useState<
    { interactor_id: string; cadence: string | null;
      opened_at: string }[]>([]);

  const [tier, setTier] = useState("follow");
  const [price, setPrice] = useState(5);
  const [amount, setAmount] = useState(5);
  const [giftNote, setGiftNote] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fail = (e: unknown) => setError(e);

  function load() {
    if (interactorToken) {
      api.subscriptions(interactorToken).then((r) => setMine(r.subscriptions))
        .catch(() => setMine([]));
      api.myOrders(interactorToken).then((r) => setOrders(r.orders))
        .catch(() => setOrders([]));
    }
    if (me && token) {
      api.subscribers("profiles", me, token)
        .then((r) => setTheirs(r.subscribers)).catch(() => setTheirs([]));
      api.gifts("profiles", me, token).then(setGifts).catch(() => setGifts(null));
      api.audience("profiles", me, token).then(setView).catch(() => setView(null));
    }
  }
  useEffect(load, [me, token, interactorToken]);
  useEffect(() => {
    if (!me || !token) return;
    api.doorsOpenTo(me, token).then((r) => setOpeners(r.openers))
      .catch(() => undefined);
  }, [me, token]);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { fail(e); } finally { setBusy(false); }
  };

  const target = subject.trim() || me;

  return (
    <div className="screen">
      <h2>{tr("aud.title", lang)}</h2>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {view && (
        <div className="card">
          <h3>{tr("aud.audience", lang)}</h3>
          <p className="small">
            {fill(tr("aud.counts", lang), {
              subs: view.subscribers, likes: view.likes,
              comments: view.comments, shares: view.shares,
            })}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{tr("aud.follow.hdr", lang)}</h3>
        <div className="row">
          <input value={subject} onChange={(e) => setSubject(e.target.value)}
                 placeholder={tr("aud.subject.ph", lang)}
                 style={{ flex: 1 }} />
          <select value={tier} onChange={(e) => setTier(e.target.value)}>
            <option value="follow">{tr("aud.tier.free", lang)}</option>
            <option value="paid">{tr("aud.tier.paid", lang)}</option>
          </select>
          {tier === "paid" && (
            <input type="number" min={1} value={price}
                   onChange={(e) => setPrice(Number(e.target.value))}
                   style={{ width: 90 }} />
          )}
          <button disabled={busy || !interactorToken || !target}
                  onClick={act(async () => {
                    await api.follow("profiles", target, tier === "paid"
                      // `accept_price` has to equal `price` exactly. It is
                      // not a flag — the point is that the number somebody
                      // agreed to is the number being charged.
                      ? { tier, price, accept_price: price,
                          beneficiary: account }
                      : { tier }, interactorToken);
                  }, tr("aud.following.said", lang))}>
            {tr("aud.follow", lang)}
          </button>
        </div>
        {tier === "paid" && (
          <p className="muted small">
            {fill(tr("aud.credited", lang), {
              account: <code>{account || tr("aud.signin", lang)}</code>,
            })}
          </p>
        )}
      </div>

      <div className="card">
        <h3>{tr("aud.youfollow", lang)}</h3>
        {mine.length === 0 &&
          <p className="muted small">{tr("aud.nothing", lang)}</p>}
        {mine.map((s) => (
          <div key={s.id}>
            <p className="small">
              {fill(tr("aud.subline", lang), {
                id: <code>{s.subject_id}</code>, tier: s.tier,
                price: s.price > 0
                  ? ` · ${s.price.toFixed(2)} ${s.currency}` : "",
                status: s.status,
              })}
            </p>
            {/* A count of deliberate acts, not a duration. */}
            <p className="muted small">
              {fill(s.periods === 1
                ? tr("aud.period", lang) : tr("aud.periods", lang),
                { n: s.periods, billing: s.billing })}
            </p>
            {s.status === "active" && (
              <div className="row">
                {s.price > 0 && (
                  <button className="chip" disabled={busy}
                          onClick={act(() => api.renewSubscription(
                            s.id, account, interactorToken),
                            tr("aud.charged.said", lang))}>
                    {tr("aud.charge", lang)}
                  </button>
                )}
                <button className="chip" disabled={busy}
                        onClick={act(() => api.unfollow(
                          "profiles", s.subject_id, interactorToken),
                          tr("aud.stopped.said", lang))}>
                  {tr("aud.stop", lang)}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("aud.whofollows", lang)}</h3>
        {theirs.length === 0 &&
          <p className="muted small">{tr("aud.nobody", lang)}</p>}
        {theirs.map((s) => (
          <p className="small" key={s.id}>
            {fill(s.periods === 1
              ? tr("aud.followerline.one", lang)
              : tr("aud.followerline", lang), {
              who: <code>{s.subscriber}</code>, tier: s.tier,
              status: s.status, n: s.periods,
            })}
          </p>
        ))}
      </div>

      {gifts && (
        <div className="card">
          <h3>{tr("aud.gifts", lang)}</h3>
          <p className="muted small">
            {fill(tr("aud.giftcap", lang),
              { cap: gifts.cap_per_gift.toFixed(2) })}
          </p>
          <div className="row">
            <input type="number" min={1} value={amount}
                   onChange={(e) => setAmount(Number(e.target.value))}
                   style={{ width: 100 }} />
            <input value={giftNote}
                   onChange={(e) => setGiftNote(e.target.value)}
                   placeholder={tr("aud.note.ph", lang)} style={{ flex: 1 }} />
            {/* No beneficiary field on purpose — the route reads it from
                the subject so a giver cannot redirect it. */}
            <button disabled={busy || !interactorToken || !target}
                    onClick={act(async () => {
                      await api.sendGift("profiles", target, {
                        amount, note: giftNote.trim() || undefined },
                        interactorToken);
                      setGiftNote("");
                    }, tr("aud.sent.said", lang))}>
              {tr("aud.sendgift", lang)}
            </button>
          </div>
          <p className="small">
            {fill(gifts.gifts.length === 1
              ? tr("aud.received.one", lang) : tr("aud.received", lang), {
              total: gifts.total_amount.toFixed(2), n: gifts.gifts.length })}
          </p>
          {gifts.gifts.map((g, i) => (
            <p className="muted small" key={g.id || i}>
              {g.amount.toFixed(2)} {g.currency}
              {g.note && ` — ${g.note}`}
            </p>
          ))}
        </div>
      )}

      <div className="card">
        <h3>{tr("aud.bought", lang)}</h3>
        <p className="muted small">{tr("aud.bought.pitch", lang)}</p>
        {orders.length === 0 &&
          <p className="muted small">{tr("aud.nothing", lang)}</p>}
        {orders.map((o, i) => (
          <p className="small" key={String(o.id ?? i)}>
            <code>{String(o.id ?? "")}</code>
            {o.price !== undefined && ` — ${String(o.price)}`}
            {o.status !== undefined && ` · ${String(o.status)}`}
          </p>
        ))}
      </div>
    
      {openers.length > 0 && (
        <div className="card">
          <h3>{tr("aud.doors", lang)}</h3>
          <p className="muted small">{tr("aud.doors.pitch", lang)}</p>
          {openers.map((o) => (
            <p key={o.interactor_id} className="muted small">
              {o.interactor_id} · {tr(
                `aud.cad.${o.cadence || "whenever"}`, lang)}
            </p>
          ))}
        </div>
      )}

</div>
  );
}
