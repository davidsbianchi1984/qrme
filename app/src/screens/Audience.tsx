import { useEffect, useState } from "react";
import { api, type AudienceView, type GiftsView, type Order,
         type Subscription } from "../api";
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

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { fail(e); } finally { setBusy(false); }
  };

  const target = subject.trim() || me;

  return (
    <div className="screen">
      <h2>Who is following, and what they pay</h2>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {view && (
        <div className="card">
          <h3>This profile's audience</h3>
          <p className="small">
            {view.subscribers} following · {view.likes} likes ·{" "}
            {view.comments} comments · {view.shares} shares
          </p>
        </div>
      )}

      <div className="card">
        <h3>Follow somebody</h3>
        <div className="row">
          <input value={subject} onChange={(e) => setSubject(e.target.value)}
                 placeholder="a profile id (blank means your own)"
                 style={{ flex: 1 }} />
          <select value={tier} onChange={(e) => setTier(e.target.value)}>
            <option value="follow">follow — free</option>
            <option value="paid">paid</option>
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
                  }, "Following.")}>Follow</button>
        </div>
        {tier === "paid" && (
          <p className="muted small">
            Credited to <code>{account || "— sign in —"}</code>. A gift reads
            who to credit from the profile itself; a subscription is told, so
            this screen shows you which account it named.
          </p>
        )}
      </div>

      <div className="card">
        <h3>What you follow</h3>
        {mine.length === 0 && <p className="muted small">Nothing yet.</p>}
        {mine.map((s) => (
          <div key={s.id}>
            <p className="small">
              <code>{s.subject_id}</code> — {s.tier}
              {s.price > 0 && ` · ${s.price.toFixed(2)} ${s.currency}`}
              {" "}· {s.status}
            </p>
            {/* A count of deliberate acts, not a duration. */}
            <p className="muted small">
              {s.periods} period{s.periods === 1 ? "" : "s"} charged, each one
              because somebody pressed a button. {s.billing}
            </p>
            {s.status === "active" && (
              <div className="row">
                {s.price > 0 && (
                  <button className="chip" disabled={busy}
                          onClick={act(() => api.renewSubscription(
                            s.id, account, interactorToken),
                            "A period charged.")}>
                    charge another period
                  </button>
                )}
                <button className="chip" disabled={busy}
                        onClick={act(() => api.unfollow(
                          "profiles", s.subject_id, interactorToken),
                          "Cancelled — the history stays.")}>
                  stop following
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Who follows this profile</h3>
        {theirs.length === 0 && <p className="muted small">Nobody yet.</p>}
        {theirs.map((s) => (
          <p className="small" key={s.id}>
            <code>{s.subscriber}</code> — {s.tier} · {s.status} ·{" "}
            {s.periods} period{s.periods === 1 ? "" : "s"}
          </p>
        ))}
      </div>

      {gifts && (
        <div className="card">
          <h3>Gifts</h3>
          <p className="muted small">
            Up to {gifts.cap_per_gift.toFixed(2)} each — published so the
            limit can be said before somebody runs into it. Gifting needs a
            verified birthdate on the giver's account: an unverified age is
            not evidence of an adult.
          </p>
          <div className="row">
            <input type="number" min={1} value={amount}
                   onChange={(e) => setAmount(Number(e.target.value))}
                   style={{ width: 100 }} />
            <input value={giftNote}
                   onChange={(e) => setGiftNote(e.target.value)}
                   placeholder="a note with it" style={{ flex: 1 }} />
            {/* No beneficiary field on purpose — the route reads it from
                the subject so a giver cannot redirect it. */}
            <button disabled={busy || !interactorToken || !target}
                    onClick={act(async () => {
                      await api.sendGift("profiles", target, {
                        amount, note: giftNote.trim() || undefined },
                        interactorToken);
                      setGiftNote("");
                    }, "Sent.")}>Send a gift</button>
          </div>
          <p className="small">
            {gifts.total.toFixed(2)} received across {gifts.gifts.length}{" "}
            {gifts.gifts.length === 1 ? "gift" : "gifts"}.
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
        <h3>What you have bought</h3>
        <p className="muted small">
          The buyer's side of the ledger. The seller's side is on the
          marketplace screen — two questions, so two lists.
        </p>
        {orders.length === 0 && <p className="muted small">Nothing yet.</p>}
        {orders.map((o, i) => (
          <p className="small" key={String(o.id ?? i)}>
            <code>{String(o.id ?? "")}</code>
            {o.price !== undefined && ` — ${String(o.price)}`}
            {o.status !== undefined && ` · ${String(o.status)}`}
          </p>
        ))}
      </div>
    </div>
  );
}
