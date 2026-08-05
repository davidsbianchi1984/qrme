import { useEffect, useState } from "react";
import { api, type Membership, type PlanCatalogue,
         type StoragePosture } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Plans — the price list, and this account's membership.
 *
 * Found by following a refusal. `Refusal.tsx` draws a plan gate as a real
 * offer: the capability that was wanted, the plan that has it, the price,
 * and the note that the billing is simulated. Then it had nowhere to send
 * anybody, because the four routes behind the price it was quoting had no
 * caller either — the console could refuse you for not having Pro and could
 * not sell you Pro. That is worse than a flat no, because it names a thing
 * that appears not to exist.
 *
 * The price list is public on purpose, and this screen keeps it that way:
 * everything above the membership card renders with no session at all.
 * `tiers.py` gives the reason — "a paywall nobody can read the terms of
 * before signing in is one people bounce off".
 *
 * Two things are shown rather than smoothed over:
 *
 * - **`visitor` and `free` are different plans that both cost nothing.** A
 *   visitor has no account and can read a public page; free has an account
 *   whose work sits in the platform's database in the clear. Collapsing them
 *   into one "$0" row — which is what a picker written from the price alone
 *   would do — would hide the entire difference.
 * - **Free and Basic run the same app.** The catalogue says so in
 *   `the_difference`, and it is rendered verbatim above the cards, because a
 *   grid of ticks invites the opposite conclusion: that $20 buys features. It
 *   buys custody.
 */
export function Plans() {
  const { session } = useSession();
  const lang = visitorLang();
  const account = session.accountId || "";
  const token = session.ownerToken || "";

  const [cat, setCat] = useState<PlanCatalogue | null>(null);
  const [mine, setMine] = useState<Membership | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.plans().then(setCat).catch(setError);
  }, []);

  function loadMine() {
    if (!account || !token) { setMine(null); return; }
    // Not an error worth a banner: reading somebody's membership needs an
    // owner token for a profile on that account, and plenty of sessions
    // here legitimately have neither.
    api.membership(account, token).then(setMine).catch(() => setMine(null));
  }
  useEffect(loadMine, [account, token]);

  async function join(plan: string) {
    setError(null); setNote(null); setBusy(true);
    try {
      const m = await api.subscribe(account, plan, token);
      setMine(m);
      setNote(tr("pln.youareon", lang)
        .replace("{title}", m.title).replace("{billing}", m.billing));
    } catch (e) { setError(e); } finally { setBusy(false); }
  }

  async function leave() {
    setError(null); setNote(null); setBusy(true);
    try {
      const m = await api.cancelMembership(account, token);
      setMine(m);
      // Said every time, because "cancel my plan" and "delete my work" are
      // the two things somebody must never confuse at this button.
      setNote(tr("pln.ended", lang));
    } catch (e) { setError(e); } finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <h2>{tr("pln.title", lang)}</h2>

      <Refusal error={error} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {cat && (
        <div className="card">
          {/* Verbatim. The sentence is the whole pricing argument, and a
              paraphrase would be a weaker version of it. */}
          <p>{cat.the_difference}</p>
          <p className="muted small">{cat.billing}</p>
        </div>
      )}

      {cat?.plans.map((p) => {
        const current = mine?.plan === p.plan;
        return (
          <div className="card" key={p.plan}>
            <h3>
              {p.title} — {p.price_usd === 0
                ? tr("pln.nocharge", lang) : `$${p.price_usd}`}
              {p.period
                ? " " + tr("pln.per", lang).replace("{period}", p.period) : ""}
              {current && <span className="pill"> {tr("pln.yourplan", lang)}</span>}
            </h3>
            <p className="small">{p.means}</p>

            <p className="muted small">
              <strong>{tr("pln.includes", lang)}</strong>{" "}
              {p.includes.length
                ? p.includes.map((c) => cat.capabilities[c]?.is || c).join("; ")
                : tr("pln.readingpublic", lang)}
            </p>
            {p.locked.length > 0 && (
              <p className="muted small">
                <strong>{tr("pln.notonplan", lang)}</strong>{" "}
                {p.locked.map((c) => cat.capabilities[c]?.is || c).join("; ")}
              </p>
            )}

            <Posture s={p.storage} lang={lang} />

            {/* `visitor` is a state, not something to buy: it is what an
                account becomes when it cancels. Offering it as a button
                would read as a plan you could downgrade into. */}
            {p.plan !== "visitor" && account && token && !current && (
              <button disabled={busy} onClick={() => join(p.plan)}>
                {p.price_usd === 0
                  ? tr("pln.movetofree", lang)
                  : tr("pln.join", lang).replace("{title}", p.title)}
              </button>
            )}
          </div>
        );
      })}

      {account && token ? (
        <div className="card">
          <h3>{tr("pln.thisaccount", lang)}</h3>
          {mine ? (
            <>
              <p className="small">
                <strong>{mine.title}</strong>
                {mine.price_usd > 0
                  ? ` — $${mine.price_usd} a ${mine.period}. ${mine.billing}`
                  : ` — ${mine.billing}`}
              </p>
              <Posture s={mine.storage} lang={lang} />
              {mine.price_usd > 0 && (
                <button disabled={busy} onClick={leave}>
                  {tr("pln.endsub", lang)}
                </button>
              )}
            </>
          ) : (
            <p className="muted small">{tr("pln.needsowner", lang)}</p>
          )}
        </div>
      ) : (
        <div className="card">
          <p className="muted small">{tr("pln.pricelist", lang)}</p>
        </div>
      )}
    </div>
  );
}

/**
 * Where the work lives on a plan.
 *
 * `disclosure` is a paragraph somebody argued carefully about what free
 * means here, and it is rendered verbatim: it is the one place the product
 * says plainly that the people who operate the deployment can read your
 * work. Summarising it into a tick would be the console taking the edge off
 * a statement the backend deliberately left sharp.
 */
function Posture({ s, lang }: { s: StoragePosture; lang: string }) {
  return (
    <>
      {/* One sentence rather than the words either side of two values: the
          clause naming who can read this does not sit last in Japanese. */}
      <p className="muted small">
        {fill(tr("pln.posture", lang), {
          title: <strong>{s.title}</strong>, means: s.means,
          who: s.who_can_read.join(", "),
        })}
      </p>
      {s.disclosure && (
        <div className="error"><p className="small">{s.disclosure}</p></div>
      )}
      {s.refused_here.length > 0 && (
        <p className="muted small">
          {fill(tr("pln.neverheld", lang), {
            list: s.refused_here.map((r) => r.replace(/_/g, " ")).join(", "),
          })}
        </p>
      )}
      <p className="muted small">
        {fill(tr("pln.erasure", lang), { how: s.custody.erasure })}
      </p>
    </>
  );
}
