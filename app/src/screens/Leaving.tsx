import { useEffect, useState } from "react";
import { api, type CloudStatus, type ContributionView,
         type DerivedAgent, type LicenseGrant,
         type RevokeResult } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * What leaves this deployment, and on what terms.
 *
 * Two different kinds of leaving, and the screen keeps them apart because
 * conflating them is how somebody agrees to the wrong one:
 *
 * - a **contribution** sends an anonymised exchange to the shared model. No
 *   ids, the persona name replaced, and a random ref so the item can be
 *   deleted at the gateway later without identifying anybody;
 * - a **licence** sends the profile itself. Somebody acquires the right to
 *   consult it, or — where the offer allows — to derive a whole new agent
 *   seeded from its persona and owned by them.
 *
 * **The contribution preview is a dry run, and says so.** `preview_next` is
 * computed whether or not the profile is opted in, so it is what *would*
 * leave rather than what is about to. Rendering it under one heading either
 * way tells an opted-out owner their next conversation is on its way out,
 * which is both alarming and false. The heading changes with `opted_in`.
 *
 * Revoking does two things and reports them separately: it stops future
 * contributions, and it asks the gateway to delete past ones by their refs.
 * `deleted_at_gateway` comes back true *vacuously* when nothing ever left —
 * a tick shown for both cases would be the wrong reassurance, so the count
 * is shown beside it.
 *
 * On the licence side, the adult bar sits **at the till**. A licence
 * permitting derivatives is refused to a buyer under 18 at acquire, not at
 * derive — the fee accrues to the seller at sale time, so refusing at
 * delivery left somebody paid for a thing the server would not hand over.
 */
export function Leaving({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";
  const buyerToken = session.interactorToken || "";

  const [status, setStatus] = useState<CloudStatus | null>(null);
  const [view, setView] = useState<ContributionView | null>(null);
  const [revoked, setRevoked] = useState<RevokeResult | null>(null);

  const [subject, setSubject] = useState("");
  const [grant, setGrant] = useState<LicenseGrant | null>(null);
  const [derived, setDerived] = useState<DerivedAgent | null>(null);

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function load() {
    api.cloudStatus().then(setStatus).catch(() => setStatus(null));
    if (me && token) {
      api.contributionView(me, token).then(setView).catch(() => setView(null));
    }
  }
  useEffect(load, [me, token]);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { setError(e); } finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>{tr("lvg.title", lang)}</h2>
      <p className="muted small">{tr("lvg.pitch", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {status && (
        <div className="card">
          <h3>{tr("lvg.sharedmodel", lang)}</h3>
          <p className="small">
            {status.cloud
              ? tr("lvg.gateway", lang)
              : tr("lvg.nogateway", lang)}
          </p>
          <p className="muted small">
            {fill(tr("lvg.fallsback", lang),
                  { to: status.fallback, note: status.contribution })}
          </p>
        </div>
      )}

      {view && (
        <div className="card">
          <h3>{tr("lvg.contributing", lang)}</h3>
          <p className="small">
            {fill(tr("lvg.profileis", lang), {
              state: <strong>
                {view.opted_in ? tr("lvg.optedin", lang) : tr("lvg.optedout", lang)}
              </strong>,
            })}
          </p>
          <p className="muted small">{view.policy}</p>

          {view.preview_next && (
            <>
              {/* The heading is conditional on purpose. The server computes
                  this preview either way, so calling it "what leaves next"
                  when the profile is opted out would be a false alarm. */}
              <h4>
                {view.opted_in
                  ? tr("lvg.wouldleave.on", lang)
                  : tr("lvg.wouldleave.off", lang)}
              </h4>
              <p className="muted small">
                {tr("lvg.dryrun", lang)}
                {!view.opted_in && " " + tr("lvg.optedoutnote", lang)}
              </p>
              {view.preview_next.exchange.map((m, i) => (
                <p className="small" key={i}>
                  <strong>{m.role}</strong>: {m.content}
                </p>
              ))}
              <p className="muted small">{tr("lvg.personareplaced", lang)}</p>
            </>
          )}

          <h4>{tr("lvg.actuallyleft", lang)}</h4>
          {view.contributed.length === 0 && (
            <p className="muted small">{tr("lvg.nothingever", lang)}</p>
          )}
          {view.contributed.map((c) => (
            <p className="small" key={c.ref}>
              <code>{c.ref}</code> · {c.at}
              {c.revoked && " " + tr("lvg.deletionrequested", lang)}
            </p>
          ))}

          <button disabled={busy || !me || !token}
                  onClick={act(async () => setRevoked(
                    await api.revokeContributions(me, token)),
                    tr("lvg.stopped", lang))}>
            {tr("lvg.stopandtake", lang)}
          </button>
          {revoked && (
            <p className="muted small">
              {/* Said apart, because true-because-nothing-left and
                  true-because-the-gateway-said-so are different facts. */}
              {revoked.revoked_count === 0
                ? tr("lvg.nothinghadleft", lang)
                : fill(revoked.deleted_at_gateway
                         ? tr("lvg.deletedatgateway", lang)
                         : tr("lvg.markedrevoked", lang),
                       { n: revoked.revoked_count })}
              {" "}{revoked.note}
            </p>
          )}
        </div>
      )}

      <div className="card">
        <h3>{tr("lvg.licensing", lang)}</h3>
        {/* "consult" is bolded inside the sentence, so the sentence is one
            row with the word as a hole — it is an adjective in English and a
            prepositional phrase in most of the others, and it does not sit
            in the same place. */}
        <p className="muted small">
          {fill(tr("lvg.otherkind", lang),
                { consult: <strong>{tr("lvg.consult", lang)}</strong> })}
        </p>
        <p className="muted small">{tr("lvg.buying", lang)}</p>
        <div className="row">
          <input value={subject} onChange={(e) => setSubject(e.target.value)}
                 placeholder={tr("lvg.subject.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !subject.trim() || !buyerToken}
                  onClick={act(async () => setGrant(
                    await api.acquireLicense(subject.trim(), buyerToken)),
                    tr("lvg.acquired", lang))}>
            {tr("lvg.acquire", lang)}
          </button>
        </div>
        {grant && (
          <>
            <p className="small">
              <code>{grant.grant_id}</code> — {grant.kind}
              {grant.terms && ` · ${grant.terms}`}
            </p>
            <p className="muted small">
              {fill(tr("lvg.keeptoken", lang),
                    { token: <code>{grant.token}</code> })}
            </p>
            {grant.can_derive ? (
              <button disabled={busy}
                      onClick={act(async () => setDerived(
                        await api.deriveAgent(grant.profile_id,
                                              grant.grant_id, buyerToken)),
                        tr("lvg.derived", lang))}>
                {tr("lvg.derive", lang)}
              </button>
            ) : (
              <p className="muted small">{tr("lvg.consultonly", lang)}</p>
            )}
          </>
        )}
        {derived && (
          <>
            <p className="small">
              {fill(tr("lvg.newprofile", lang), {
                id: <code>{derived.derived_profile_id}</code>,
                src: <code>{derived.licensed_from}</code>,
              })}
            </p>
            <p className="muted small">
              {fill(tr("lvg.keepowner", lang),
                    { token: <code>{derived.owner_token}</code> })}
            </p>
            <p className="muted small">{tr("lvg.oneagent", lang)}</p>
          </>
        )}
      </div>
    </div>
  );
}
