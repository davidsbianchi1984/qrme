import { useEffect, useState } from "react";
import { api, type CloudStatus, type ContributionView,
         type DerivedAgent, type LicenseGrant,
         type RevokeResult } from "../api";
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
      <h2>What leaves, and on what terms</h2>
      <p className="muted small">
        Two different kinds of leaving. One sends an exchange with the names
        taken out; the other sends the profile itself.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {status && (
        <div className="card">
          <h3>The shared model</h3>
          <p className="small">
            {status.cloud
              ? "A gateway is configured on this deployment."
              : "No gateway is configured, so nothing can leave even if a "
                + "profile is opted in."}
          </p>
          <p className="muted small">
            Falls back to {status.fallback}. {status.contribution}
          </p>
        </div>
      )}

      {view && (
        <div className="card">
          <h3>Contributing</h3>
          <p className="small">
            This profile is <strong>
              {view.opted_in ? "opted in" : "opted out"}
            </strong>.
          </p>
          <p className="muted small">{view.policy}</p>

          {view.preview_next && (
            <>
              {/* The heading is conditional on purpose. The server computes
                  this preview either way, so calling it "what leaves next"
                  when the profile is opted out would be a false alarm. */}
              <h4>
                {view.opted_in
                  ? "What would leave on the next thumbs-up"
                  : "What would leave if you turned this back on"}
              </h4>
              <p className="muted small">
                A dry run — nothing has been sent to produce this.
                {!view.opted_in && " This profile is opted out, so nothing "
                  + "is going anywhere."}
              </p>
              {view.preview_next.exchange.map((m, i) => (
                <p className="small" key={i}>
                  <strong>{m.role}</strong>: {m.content}
                </p>
              ))}
              <p className="muted small">
                Note the persona name is already replaced. That is what the
                gateway would receive, not a summary of it.
              </p>
            </>
          )}

          <h4>What has actually left</h4>
          {view.contributed.length === 0 && (
            <p className="muted small">Nothing, ever.</p>
          )}
          {view.contributed.map((c) => (
            <p className="small" key={c.ref}>
              <code>{c.ref}</code> · {c.at}
              {c.revoked && " · deletion requested"}
            </p>
          ))}

          <button disabled={busy || !me || !token}
                  onClick={act(async () => setRevoked(
                    await api.revokeContributions(me, token)),
                    "Stopped.")}>
            Stop, and take back what has left
          </button>
          {revoked && (
            <p className="muted small">
              {/* Said apart, because true-because-nothing-left and
                  true-because-the-gateway-said-so are different facts. */}
              {revoked.revoked === 0
                ? "Nothing had ever left, so there was nothing to delete."
                : revoked.deleted_at_gateway
                  ? `${revoked.revoked} item(s) requested deleted at the `
                    + "gateway."
                  : `${revoked.revoked} item(s) are marked revoked here, but `
                    + "no gateway was reachable to delete them."}
              {" "}{revoked.note}
            </p>
          )}
        </div>
      )}

      <div className="card">
        <h3>Licensing a profile</h3>
        <p className="muted small">
          The other kind of leaving. A <strong>consult</strong> licence buys
          time with the profile; a licence that permits derivatives lets you
          build a new agent seeded from its persona, owned by you and marked
          with where it came from.
        </p>
        <p className="muted small">
          Buying one needs your token as a person, not as a profile's owner.
          A licence permitting derivatives is refused to a buyer under 18 at
          the till rather than at delivery — the fee moves when the licence
          is sold.
        </p>
        <div className="row">
          <input value={subject} onChange={(e) => setSubject(e.target.value)}
                 placeholder="the profile to license" style={{ flex: 1 }} />
          <button disabled={busy || !subject.trim() || !buyerToken}
                  onClick={act(async () => setGrant(
                    await api.acquireLicense(subject.trim(), buyerToken)),
                    "Acquired.")}>
            Acquire a licence
          </button>
        </div>
        {grant && (
          <>
            <p className="small">
              <code>{grant.grant_id}</code> — {grant.kind}
              {grant.terms && ` · ${grant.terms}`}
            </p>
            <p className="muted small">
              Keep the licence token: <code>{grant.token}</code>
            </p>
            {grant.can_derive ? (
              <button disabled={busy}
                      onClick={act(async () => setDerived(
                        await api.deriveAgent(grant.profile_id,
                                              grant.grant_id, buyerToken)),
                        "Derived.")}>
                Derive an agent from it
              </button>
            ) : (
              <p className="muted small">
                Consult only — this licence does not permit deriving an
                agent, and the button is absent rather than present and
                refused.
              </p>
            )}
          </>
        )}
        {derived && (
          <>
            <p className="small">
              New profile <code>{derived.derived_profile_id}</code>, yours,
              licensed from <code>{derived.licensed_from}</code>.
            </p>
            <p className="muted small">
              Keep this owner token — it is shown once:{" "}
              <code>{derived.owner_token}</code>
            </p>
            <p className="muted small">
              One agent per licence. Deriving again from the same grant is a
              409, because a licence was sold for one.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
